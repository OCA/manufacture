# -*- coding: utf-8 -*-
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    @api.multi
    def _create_qc_trigger(self):
        self.ensure_one()
        qc_trigger = {
            'name': self.name,
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
            for rec in self:
                qc_triggers = qc_trigger_model.search(
                    [('picking_type', '=', rec.id)])
                qc_triggers.write({'name': rec.name})
        return res
