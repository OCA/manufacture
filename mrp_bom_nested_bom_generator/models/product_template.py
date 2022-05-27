from odoo import _, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    nested_bom_ids = fields.One2many(
        comodel_name="mrp.nested.bom",
        inverse_name="parent_id",
    )
    nested_bom_count = fields.Integer(
        compute="_compute_nested_bom_count",
        string="Nested Bom Count",
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
                "parent_id": self.id,
                "product_tmpl_id": self.id,
                "product_qty": 1,
                "uom_id": self.uom_id.id,
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

    def create_boms(self) -> None:
        """
        Create BOM for stage
        :return None
        """
        for product, component in self.group_by_stage():
            self.env["mrp.bom"].create(
                {
                    "product_tmpl_id": product.product_tmpl_id.id,
                    "product_uom_id": product.uom_id.id,
                    "product_qty": product.product_qty,
                    "type": "normal",
                    "bom_line_ids": component._prepare_bom_lines(product),
                }
            )

    def action_generate_nested_boms(self) -> None:
        """
        Generate MRP BOM by nested BOM
        :raise UserError Nested BOM is Empty
        :return None
        """
        self.ensure_one()
        if self.nested_bom_count > 0:
            self.nested_bom_ids._prepare_product_attribute()
            self.create_boms()
            return
        raise models.UserError(_("Nested BOM is Empty!"))
