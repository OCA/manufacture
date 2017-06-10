# -*- coding: utf-8 -*-
# Copyright 2017 Bima Wijaya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    property_ids = fields.Many2many('mrp.property',
                                    'procurement_property_rel',
                                    'procurement_id', 'property_id',
                                    string='Properties')

    @api.multi
    def _get_matching_bom(self):
        res = super(ProcurementOrder, self.with_context(
            property_ids=[p.id for p in self.property_ids])).\
            _get_matching_bom()
        return res

    @api.multi
    def make_mo(self):
        res = super(ProcurementOrder, self).make_mo()
        production_obj = self.env['mrp.production']
        for procurement_id, produce_id in res.iteritems():
            procurement = self.browse(procurement_id)
            production = production_obj.browse(produce_id)
            vals = {
                'property_ids': [
                    (6, 0, [x.id for x in procurement.property_ids])
                ]
            }
            production.write(vals)
        return res
