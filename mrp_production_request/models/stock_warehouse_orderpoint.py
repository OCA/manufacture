# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _quantity_in_progress(self):
        res = super(Orderpoint, self)._quantity_in_progress()
        mrp_requests = self.env['mrp.production.request'].search([
            ('state', 'not in', ('done', 'cancel')),
            ('orderpoint_id', 'in', self.ids),
        ])
        for rec in mrp_requests:
            res[rec.orderpoint_id.id] += rec.product_uom_id._compute_quantity(
                rec.pending_qty, rec.orderpoint_id.product_uom, round=False)
        return res
