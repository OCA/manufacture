from odoo import _, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    nested_bom = fields.Boolean(string="Nested BOM")

    nested_bom_line_ids = fields.One2many(
        string="Nested BOM Lines",
        comodel_name="mrp.nested.bom.line",
        inverse_name="bom_id",
    )

    parent_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="Parent MRP BOM",
        index=True,
    )

    child_ids = fields.One2many(
        comodel_name="mrp.bom", inverse_name="parent_id", string="Children BOMs"
    )

    def _prepare_temp_nested_bom_item(self) -> models.Model:
        """
        Prepare temp nested bom for current product template
        :return temp nested bom record
        :rtype mrp.nested.bom.line()
        """
        return self.nested_bom_line_ids.new(
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
        ] + list(self.nested_bom_line_ids.sorted(lambda line: line.sequence))
        for i in range(1, len(nestings)):
            yield nestings[i - 1], nestings[i]

    def unlink_existing_bom(self) -> bool:
        """
        Unlink unused BOMs
        Archive used BOM
        Unlink all components in current BOM
        :return: bool
        """
        child_ids = self.child_ids
        if not child_ids:
            return False
        mrp_bom_used_ids = (
            self.env["mrp.production"]
            .search([("bom_id", "in", child_ids.ids)])
            .mapped("bom_id")
        )
        mrp_bom_unused_ids = child_ids.filtered(
            lambda bom: bom.id not in mrp_bom_used_ids.ids
        )
        mrp_bom_used_ids.sudo().write({"active": False})
        mrp_bom_unused_ids.sudo().unlink()
        self.bom_line_ids.sudo().unlink()
        return True

    def _create_mrp_bom_record(self, nested_bom, lines):
        """
        Create mrp.bom record for product
        :param models.Model nested_bom: mrp.nested.bom.line record
        :param list lines: x2m “create” command
        :return bool: bool
        """
        if not lines or not nested_bom:
            return False
        if not all(len(line) == 3 for line in lines):
            return False
        if not all(not bool(c) and isinstance(v, dict) and v for c, _, v in lines):
            return False
        self.env["mrp.bom"].create(
            {
                "parent_id": self.id,
                "product_tmpl_id": nested_bom.product_tmpl_id.id,
                "product_uom_id": nested_bom.uom_id.id,
                "product_qty": nested_bom.product_qty,
                "type": "normal",
                "bom_line_ids": lines,
            }
        )
        return True

    def create_child_boms(self) -> None:
        """
        Patch components in current BOM and create child BOMs
        :return None
        """
        self.unlink_existing_bom()
        for index, arg in enumerate(self.group_by_stage()):
            nested_bom, component = arg
            bom_lines = component._prepare_bom_lines(nested_bom)
            key = "bom_product_template_attribute_value_ids"
            line_ptavs = [val[key] for _, _, val in bom_lines]
            if all(line_ptavs) or len(bom_lines) == 1:
                if bool(index):
                    self._create_mrp_bom_record(nested_bom, bom_lines)
                else:
                    self.update({"bom_line_ids": bom_lines})
                continue
            for line in bom_lines:
                if bool(index):
                    self._create_mrp_bom_record(nested_bom, [line])
                else:
                    self.update({"bom_line_ids": [line]})

    def action_generate_mrp_boms(self) -> bool:
        """
        Generate MRP BOM by nested BOM
        :raise UserError Nested BOM is Empty
        :return bool
        """
        self.ensure_one()
        if not self.nested_bom_line_ids:
            raise models.UserError(_("Nested BOM is Empty!"))
        self.nested_bom_line_ids._prepare_product_attribute()
        self.create_child_boms()
        return True

    def action_open_parent_bom(self):
        """Action open parent mrp bom record"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_id": self.parent_id.id,
            "res_model": "mrp.bom",
            "target": "current",
            "views": [(False, "form")],
        }
