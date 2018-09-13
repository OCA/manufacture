# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    created_mrp_production_request_id = fields.Many2one(
        comodel_name='mrp.production.request',
        string='Created Production Request',
    )

    @api.model
    def create(self, vals):
        if 'production_id' in vals:
            production = self.env['mrp.production'].browse(
                vals['production_id'])
            if production.mrp_production_request_id:
                vals['propagate'] = False
        return super(StockMove, self).create(vals)
