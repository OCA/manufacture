# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, api


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.model_create_multi
    def create(self, vals_list):
        refurbish_location_dest_id = self.env.context.get(
            'force_refurbish_location_dest_id', False)
        if refurbish_location_dest_id:
            for vals in vals_list:
                vals['location_dest_id'] = refurbish_location_dest_id
        return super(StockMove, self).create(vals_list)
