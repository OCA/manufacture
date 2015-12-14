# -*- coding: utf-8 -*-
# © 2015 Avanzosc
# © 2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields


class MrpProductionWorkcenterLine(models.Model):

    _inherit = 'mrp.production.workcenter.line'
    operation_time_lines = fields.One2many(
        'operation.time.line', 'operation_time', string='Operation Time Lines')

    def _create_operation_line(self):
        self.env['operation.time.line'].create({
            'start_date': fields.Datetime.now(),
            'operation_time': self.id,
            'user': self.env.uid})

    def _write_end_date_operation_line(self):
        self.operation_time_lines[-1].end_date = fields.Datetime.now()

    @api.multi
    def action_start_working(self):
        result = super(MrpProductionWorkcenterLine,
                       self).action_start_working()
        self._create_operation_line()
        return result

    @api.multi
    def action_pause(self):
        result = super(MrpProductionWorkcenterLine, self).action_pause()
        self._write_end_date_operation_line()
        return result

    @api.multi
    def action_resume(self):
        result = super(MrpProductionWorkcenterLine, self).action_resume()
        self._create_operation_line()
        return result

    @api.multi
    def action_done(self):
        not_paused_records = self.filtered(lambda x: x.state != 'pause')
        result = super(MrpProductionWorkcenterLine, self).action_done()
        not_paused_records._write_end_date_operation_line()
        return result


class OperationTimeLine(models.Model):
    _name = 'operation.time.line'
    _rec_name = 'operation_time'

    def _default_user(self):
        return self.env.uid

    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    operation_time = fields.Many2one('mrp.production.workcenter.line')
    uptime = fields.Float(
        string='Machine up time', compute='_compute_uptime', store=True,
        digits=(12, 6))
    production = fields.Many2one(
        'mrp.production', related='operation_time.production_id',
        string='Production', store=True)
    user = fields.Many2one('res.users', string='User', default=_default_user)

    @api.one
    @api.depends('start_date', 'end_date')
    def _compute_uptime(self):
        if self.end_date and self.start_date:
            timedelta = fields.Datetime.from_string(self.end_date) - \
                fields.Datetime.from_string(self.start_date)
            self.uptime = timedelta.total_seconds() / 3600.
