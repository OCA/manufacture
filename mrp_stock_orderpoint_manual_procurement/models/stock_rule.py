# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom,
                         location_id, name, origin, values, bom):
        res = super(StockRule, self)._prepare_mo_vals(
            product_id, product_qty, product_uom, location_id, name,
            origin, values, bom)
        requested_uid = self.env.context.get('requested_uid')
        if requested_uid:
            res.update({'requested_by': requested_uid.id})
        return res
