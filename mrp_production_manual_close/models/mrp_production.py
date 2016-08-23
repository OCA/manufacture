# -*- coding: utf-8 -*-
# (c) 2015 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def button_produce_close(self):
        self.ensure_one()
        proc_obj = self.env['procurement.order']
        if self.move_created_ids:
            self.move_created_ids.action_cancel()
        procs = proc_obj.search([('move_dest_id', 'in', self.move_lines.ids)])
        if procs:
            procs.cancel()
        self.move_lines.action_cancel()
        procs = proc_obj.search([('production_id', '=', self.id)])
        for proc in procs:
            proc.message_post(body=_('Manufacturing order cancelled.'))
            proc.state = 'exception'
        self.signal_workflow('button_produce_close')
