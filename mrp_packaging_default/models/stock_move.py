# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _packaging_vals_from_bom_line(self, vals):
        """Fill vals with packaging info from BoM line."""
        try:
            bom_line = self.env["mrp.bom.line"].browse(vals["bom_line_id"])
        except KeyError:
            # No BoM line, nothing to do
            return
        vals.update(
            {
                "product_packaging_id": bom_line.product_packaging_id.id,
                "product_packaging_qty": bom_line.product_packaging_qty,
            }
        )

    @api.model_create_multi
    def create(self, vals_list):
        """Inherit packaging from BoM line."""
        for vals in vals_list:
            self._packaging_vals_from_bom_line(vals)
        return super().create(vals_list)

    def write(self, vals):
        """Inherit packaging from BoM line."""
        self._packaging_vals_from_bom_line(vals)
        return super().write(vals)
