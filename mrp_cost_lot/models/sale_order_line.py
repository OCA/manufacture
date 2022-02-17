# Copyright 2022 Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        for line in self.filtered(
            lambda l: l.lot_id and l.lot_id.standard_price != 0
        ).sudo():
            product = line.product_id.with_company(line.company_id)
            price = line.lot_id.standard_price
            currency = line.currency_id or line.order_id.currency_id
            line.purchase_price = product.cost_currency_id._convert(
                    from_amount=price,
                    to_currency=currency,
                    company=line.company_id or self.env.company,
                    date=line.order_id.date_order or fields.Date.today(),
                    round=False,
                ) if currency and price else price

