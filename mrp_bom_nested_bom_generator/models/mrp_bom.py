from odoo import _, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    bom_type_nested = fields.Boolean(string="Type Nested BOM", default=False)
    changed_nested_bom = fields.Boolean(string="Changed Nested Bom", default=True)

    nested_bom_ids = fields.One2many(
        comodel_name="mrp.nested.bom",
        inverse_name="bom_id",
    )

    nested_bom_count = fields.Integer(
        compute="_compute_nested_bom_count",
        string="Nested Bom Count",
    )

    parent_bom_id = fields.Many2one(comodel_name="mrp.bom", string="Parent MRP BOM")

    child_bom_ids = fields.One2many(
        comodel_name="mrp.bom", inverse_name="parent_bom_id", string="Child MRP BOM"
    )

    def _compute_nested_bom_count(self) -> None:
        """
        Compute count nested BOM lines
        :return None
        """
        for rec in self:
            rec.nested_bom_count = len(rec.nested_bom_ids)

    def _prepare_temp_nested_bom_item(self) -> models.Model:
        """
        Prepare temp nested bom for current product template
        :return temp nested bom record
        :rtype mrp.nested.bom()
        """
        return self.nested_bom_ids.new(
            {
                "parent_id": self.product_tmpl_id.id,
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
        Unlink BOM by product.template
        :return: bool
        """
        mrp_bom_ids = self.child_bom_ids
        if not len(mrp_bom_ids) > 0:
            return False
        used_mrp_bom_ids = (
            self.env["mrp.production"]
            .search([("bom_id", "in", mrp_bom_ids.ids)])
            .mapped("bom_id")
        )
        unused_mrp_bom_ids = mrp_bom_ids.filtered(
            lambda bom: bom.id not in used_mrp_bom_ids.ids
        )
        used_mrp_bom_ids.sudo().write({"active": False})
        unused_mrp_bom_ids.sudo().unlink()
        self.bom_line_ids.sudo().unlink()
        # TODO доделать
        return True

    def _create_mrp_bom_record(self, product, lines):
        """
        Create mrp.bom record by product record and bom lines
        :param models.Model product: product.template record
        :param list lines: list [(0, 0, vals), ...]
        """
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

    def _append_bom_line_components(self, lines, **kwargs):
        """Update record components"""
        self.write({"bom_line_ids": lines})

    def create_boms(self) -> None:
        """
        Create BOM for stage
        :return None
        """
        self.unlink_existing_bom()
        for index, arg in enumerate(self.group_by_stage(), start=1):
            product, component = arg
            bom_lines = component._prepare_bom_lines(product)
            line_ptavs = [
                line[2]["bom_product_template_attribute_value_ids"]
                for line in bom_lines
            ]
            func = (
                self._append_bom_line_components
                if index == 1
                else self._create_mrp_bom_record
            )
            if all(line_ptavs) or len(bom_lines) == 1:
                func(product=product, lines=bom_lines)
                continue
            for line in bom_lines:
                func(
                    product=product,
                    lines=[
                        line,
                    ],
                )

    def action_generate_nested_boms(self) -> bool:
        """
        Generate MRP BOM by nested BOM
        :raise UserError Nested BOM is Empty
        :return bool
        """
        self.ensure_one()
        if not self.nested_bom_count > 0:
            raise models.UserError(_("Nested BOM is Empty!"))
        if not self.changed_nested_bom:
            return False
        self.nested_bom_ids._prepare_product_attribute()
        self.create_boms()
        self.changed_nested_bom = False
        return True

    def action_parent_bom(self):
        """Action open parent mrp bom record"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_id": self.parent_bom_id.id,
            "res_model": "mrp.bom",
            "target": "current",
            "views": [(False, "form")],
        }
