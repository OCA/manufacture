# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    component_unit_sale_price = fields.Float(
        compute="_compute_component_unit_sale_price",
        store=True,
    )
    display_component_unit_sale_price = fields.Float(
        string="Component Sales Price",
        compute="_compute_display_component_unit_sale_price",
        inverse="_inverse_display_component_unit_sale_price",
        store=True,
    )
    component_total_sale_price = fields.Float(
        compute="_compute_component_total_sale_price",
        inverse="_inverse_component_total_sale_price",
        store=True,
    )

    @api.depends("product_id")
    def _compute_component_unit_sale_price(self):
        for record in self:
            if record.product_id:
                record.component_unit_sale_price = record.product_id.lst_price
            else:
                record.component_unit_sale_price = 0

    @api.depends("component_unit_sale_price")
    def _compute_display_component_unit_sale_price(self):
        for record in self:
            record.display_component_unit_sale_price = record.component_unit_sale_price

    @api.depends("display_component_unit_sale_price", "product_qty")
    def _compute_component_total_sale_price(self):
        for record in self:
            record.component_total_sale_price = (
                record.display_component_unit_sale_price * record.product_qty
            )

    def _inverse_display_component_unit_sale_price(self):
        for record in self:
            record.component_unit_sale_price = record.display_component_unit_sale_price

    def _inverse_component_total_sale_price(self):
        for record in self:
            record.display_component_unit_sale_price = (
                record.component_total_sale_price / record.product_qty
            )
