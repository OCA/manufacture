from odoo import _, api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    nested_bom = fields.Boolean(string="Nested BOM")
    nested_bom_updated = fields.Boolean(
        string="Changed Nested Bom",
        compute="_compute_nested_bom_updated",
        store=True,
        default=True,
    )

    nested_bom_ids = fields.One2many(
        comodel_name="mrp.nested.bom",
        inverse_name="bom_id",
    )

    parent_bom_id = fields.Many2one(comodel_name="mrp.bom", string="Parent MRP BOM")

    child_bom_ids = fields.One2many(
        comodel_name="mrp.bom", inverse_name="parent_bom_id", string="Child BOMs"
    )

    CHOICE_FUNC = {True: "_create_mrp_bom_record", False: "_append_bom_line_components"}

    @api.depends("nested_bom_ids")
    def _compute_nested_bom_updated(self):
        self.write({"nested_bom_updated": True})

    def _prepare_temp_nested_bom_item(self) -> models.Model:
        """
        Prepare temp nested bom for current product template
        :return temp nested bom record
        :rtype mrp.nested.bom()
        """
        return self.nested_bom_ids.new(
            {
                "bom_product_tmpl_id": self.product_tmpl_id.id,
                "product_tmpl_id": self.product_tmpl_id.id,
                "product_qty": 1,
                "uom_id": self.product_tmpl_id.uom_id.id,
            }
        )

    def group_by_stage(self) -> list:
        """
        Group nested bom line by stage
        :yield list(MRP product, component)
        :
        """
        nestings = [
            self._prepare_temp_nested_bom_item(),
        ] + list(self.nested_bom_ids.sorted(lambda line: line.sequence))
        for i in range(1, len(nestings)):
            yield nestings[i - 1], nestings[i]

    def unlink_existing_bom(self) -> bool:
        """
        Unlink unused BOMs
        Archive used BOM
        Unlink all components in current BOM
        :return: bool
        """
        child_bom_ids = self.child_bom_ids
        if not child_bom_ids:
            return False
        mrp_bom_used_ids = (
            self.env["mrp.production"]
            .search([("bom_id", "in", child_bom_ids.ids)])
            .mapped("bom_id")
        )
        mrp_bom_unused_ids = child_bom_ids.filtered(
            lambda bom: bom.id not in mrp_bom_used_ids.ids
        )
        mrp_bom_used_ids.sudo().write({"active": False})
        mrp_bom_unused_ids.sudo().unlink()
        self.bom_line_ids.sudo().unlink()
        return True

    def _create_mrp_bom_record(self, product, lines):
        """
        Create mrp.bom record for product
        :param models.Model product: product.product record
        :param list lines: x2m “create” command
        :return bool: bool
        """
        if not lines or not product:
            return
        if not all(len(line) == 3 for line in lines):
            return False
        if not all(not bool(c) and isinstance(v, dict) and v for c, _, v in lines):
            return False
        self.env["mrp.bom"].create(
            {
                "parent_bom_id": self.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_uom_id": product.uom_id.id,
                "product_qty": product.product_qty,
                "type": "normal",
                "bom_line_ids": lines,
            }
        )
        return True

    def _append_bom_line_components(self, lines, **__):
        """Update record components"""
        self.write({"bom_line_ids": lines})

    def create_boms(self) -> None:
        """
        Create Nested BOMs and unlink/archive old BOMs
        :return None
        """
        self.unlink_existing_bom()
        for index, arg in enumerate(self.group_by_stage()):
            product, component = arg
            bom_lines = component._prepare_bom_lines(product)
            key = "bom_product_template_attribute_value_ids"
            line_ptavs = [val[key] for _, _, val in bom_lines]
            func = getattr(self, self.CHOICE_FUNC[bool(index)])
            if all(line_ptavs) or len(bom_lines) == 1:
                func(product=product, lines=bom_lines)
                continue
            for line in bom_lines:
                func(product=product, lines=[line])

    def action_generate_nested_boms(self) -> bool:
        """
        Generate MRP BOM by nested BOM
        :raise UserError Nested BOM is Empty
        :return bool
        """
        self.ensure_one()
        if not len(self.nested_bom_ids) > 0:
            raise models.UserError(_("Nested BOM is Empty!"))
        if not self.nested_bom_updated:
            return False
        self.nested_bom_ids._prepare_product_attribute()
        self.create_boms()
        self.nested_bom_updated = False
        return True

    def action_open_parent_bom(self):
        """Action open parent mrp bom record"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_id": self.parent_bom_id.id,
            "res_model": "mrp.bom",
            "target": "current",
            "views": [(False, "form")],
        }
