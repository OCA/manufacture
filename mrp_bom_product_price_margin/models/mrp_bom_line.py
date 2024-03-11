# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    # New fields
    standard_price_unit = fields.Float(compute="_compute_standard_price_unit")
    currency_id = fields.Many2one(related="product_id.currency_id")

    standard_price_subtotal = fields.Float(
        string="Subtotal price", compute="_compute_standard_price_subtotal"
    )
    # Percentage float, so 25% is 0,25. For one number behind decimal, needs 3 digits
    standard_price_subtotal_percentage = fields.Float(
        string="Subtotal price %",
        compute="_compute_standard_price_subtotal_percentage",
        digits=(16, 3),
    )

    @api.depends("standard_price_unit", "product_qty")
    def _compute_standard_price_subtotal(self):
        for line in self:
            line.standard_price_subtotal = line.standard_price_unit * line.product_qty

    @api.depends("product_id")
    def _compute_standard_price_unit(self):
        for line in self:
            line.standard_price_unit = line.product_id.standard_price

    @api.depends(
        "standard_price_subtotal", "bom_id.bom_line_ids.standard_price_subtotal"
    )
    def _compute_standard_price_subtotal_percentage(self):
        for line in self:
            bom = line.bom_id
            total_price = sum(line.standard_price_subtotal for line in bom.bom_line_ids)
            line.standard_price_subtotal_percentage = (
                line.standard_price_subtotal / total_price if total_price != 0 else 0
            )
