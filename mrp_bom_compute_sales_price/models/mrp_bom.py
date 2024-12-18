# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    product_sale_price = fields.Float(compute="_compute_product_sale_price", store=True)
    display_product_sale_price = fields.Float(string="Sales price")

    @api.depends("bom_line_ids.component_unit_sale_price")
    def _compute_product_sale_price(self):
        for record in self:
            record.product_sale_price = 0
            if record.bom_line_ids:
                for line in record.bom_line_ids:
                    record.product_sale_price += line.component_total_sale_price
            else:
                record.product_sale_price = 0
            record.display_product_sale_price = record.product_sale_price

    def action_set_product_sale_price(self):
        if self.product_id:
            self.product_id.lst_price = self.display_product_sale_price
        else:
            self.product_tmpl_id.list_price = self.display_product_sale_price

    def action_calculate_product_sale_price(self):
        for record in self:
            record.display_product_sale_price = 0
            if record.bom_line_ids:
                for line in record.bom_line_ids:
                    record.display_product_sale_price += line.component_total_sale_price
            else:
                record.display_product_sale_price = 0
