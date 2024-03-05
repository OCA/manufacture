from odoo import api, fields, models


class MrpBomConfigured(models.TransientModel):
    _name = "mrp.bom.configured"
    _description = "Resulting BoM from an input line"

    input_line_id = fields.Many2one(
        comodel_name="input.line", default=lambda self: self._default_config_id()
    )
    line_ids = fields.One2many(
        comodel_name="mrp.bom.line.configured",
        compute="_compute_line_ids",
        inverse_name="bom_id",
        default=lambda self: self._default_line_ids()
    )
    product_id = fields.Many2one(
        comodel_name="product.configured",
        default=lambda self: self._default_product_id(),
    )

    @api.model
    def _default_config_id(self):
        return self.env.context.get("active_id")

    @api.model
    def _default_product_id(self):
        input_line_id = self.env["input.line"].browse(
            self.env.context.get("active_id")
        )
        config_id = input_line_id.config_id
        new_product = self.env["product.configured"].create(
            {
                "name": f"{config_id.name} - {input_line_id.name}",
            }
        )
        return new_product.id

    def _default_line_ids(self):
        input_line_id = self.env["input.line"].browse(
            self.env.context.get("active_id")
        )
        components, _ = input_line_id._get_filtered_components_from_values()
        lines = []
        for comp in components:
            quantity = (
                comp.compute_qty_from_formula(input_line_id)
                if comp.use_formula_compute_qty
                else comp.product_qty
            )
            # price += quantity * comp.product_id.lst_price
            lines.append(self.env["mrp.bom.line.configured"].create(
                {
                    "product_id": comp.product_id.id,
                    "product_qty": quantity,
                }
            ).id)

        return lines


class MrpBomLineConfigured(models.TransientModel):
    _name = "mrp.bom.line.configured"
    _description = "Resulting BoM line from an input line"

    bom_id = fields.Many2one(comodel_name="mrp.bom.configured", ondelete="cascade")
    product_id = fields.Many2one(comodel_name="product.product")
    product_qty = fields.Float(string="Quantity")


class ProductConfigured(models.TransientModel):
    _name = "product.configured"
    _description = "Product stub for the configured bom"

    name = fields.Char()
