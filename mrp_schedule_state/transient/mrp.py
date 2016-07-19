# -*- coding: utf-8 -*-
##############################################################################
#
#  license AGPL version 3 or later
#  see license in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp import models, api, fields


class SwitchScheduleState(models.TransientModel):
    _name = 'switch.schedule_state'

    @api.model
    def _get_state(self):
        active_ids = self.env.context.get('active_ids', [])
        manufacturing_orders = self.env['mrp.production'].browse(active_ids)
        result = manufacturing_orders._get_values_from_selection(
            'schedule_state')
        return result

    schedule_state = fields.Selection(
        _get_state,
        string='Schedule State',
        required=True)

    @api.multi
    def switch_schedule_state(self):
        self.ensure_one()
        MrpProduction = self.env['mrp.production']
        active_ids = self.env.context.get('active_ids', [])
        vals = {'schedule_state': self.schedule_state}
        manufacturing_orders = self.env['mrp.production'].browse(active_ids)
        manufacturing_orders.write(vals)
        return True
