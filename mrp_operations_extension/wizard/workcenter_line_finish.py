# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class WorkcenterLineFinish(models.TransientModel):
    _name = "workcenter.line.finish"

    @api.multi
    def make_them_done(self):
        if ('active_id' in self.env.context and
                (self.env.context['active_model'] ==
                 'mrp.production.workcenter.line')):
            wc_line_obj = self.env['mrp.production.workcenter.line']
            wc_line = wc_line_obj.browse(self.env.context['active_id'])
            wc_line.move_lines.filtered(
                lambda x: x.state not in ('cancel', 'done')).action_done()
            wc_line.signal_workflow('button_done')

    @api.multi
    def cancel_all(self):
        if ('active_id' in self.env.context and
                (self.env.context['active_model'] ==
                 'mrp.production.workcenter.line')):
            wc_line_obj = self.env['mrp.production.workcenter.line']
            wc_line = wc_line_obj.browse(self.env.context['active_id'])
            wc_line.move_lines.filtered(
                lambda x: x.state not in ('cancel', 'done')).action_cancel()
            if wc_line.do_production:
                wc_line.production_id.move_created_ids.filtered(
                    lambda x: x.state not in
                    ('cancel', 'done')).action_cancel()
                wc_line.production_id.refresh()
            wc_line.signal_workflow('button_done')
