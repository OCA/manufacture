# -*- coding: utf-8 -*-
# (c) 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    @api.multi
    def _create_qc_trigger(self):
        qc_trigger = {
            'name': self.complete_name,
            'company_id': self.warehouse_id.company_id.id,
            'picking_type': self.id,
            'partner_selectable': True,
        }
        return self.env['qc.trigger'].sudo().create(qc_trigger)

    @api.model
    def create(self, vals):
        picking_type = super(StockPickingType, self).create(vals)
        picking_type._create_qc_trigger()
        return picking_type

    @api.multi
    def write(self, vals):
        res = super(StockPickingType, self).write(vals)
        if vals.get('name') or vals.get('warehouse_id'):
            qc_trigger_model = self.env['qc.trigger'].sudo()
            qc_trigger = qc_trigger_model.search(
                [('picking_type', '=', self.id)])
            qc_trigger.name = self.complete_name
        return res
