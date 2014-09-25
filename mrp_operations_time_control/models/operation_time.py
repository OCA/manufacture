# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import api, models, fields


class MrpProductionWorkcenterLine(models.Model):

    _inherit = 'mrp.production.workcenter.line'
    operation_time_lines = fields.One2many('operation.time.line',
                                           'operation_time',
                                           string='Operation Time Lines')

    def _create_operation_line(self):
        self.env['operation.time.line'].create({
            'start_date': fields.Datetime.now(),
            'operation_time': self.id,
            'user': self.env.uid})

    def _write_end_date_operation_line(self):
        self.operation_time_lines[-1].end_date = fields.Datetime.now()

    def action_start_working(self):
        result = super(MrpProductionWorkcenterLine,
                       self).action_start_working()
        self._create_operation_line()
        return result

    def action_pause(self):
        result = super(MrpProductionWorkcenterLine, self).action_pause()
        self._write_end_date_operation_line()
        return result

    def action_resume(self):
        result = super(MrpProductionWorkcenterLine, self).action_resume()
        self._create_operation_line()
        return result

    def action_done(self):
        result = super(MrpProductionWorkcenterLine, self).action_done()
        self._write_end_date_operation_line()
        return result


class OperationTimeLine(models.Model):

    _name = 'operation.time.line'
    _rec_name = 'operation_time'

    def _default_user(self):
        return self.env.uid

    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    operation_time = fields.Many2one('mrp.production.workcenter.line')
    uptime = fields.Float(string='Uptime', compute='operation_uptime',
                          store=True, digits=(12, 6))
    production = fields.Many2one('mrp.production',
                                 related='operation_time.production_id',
                                 string='Production', store=True)
    user = fields.Many2one('res.users', string='User', default=_default_user)

    @api.one
    @api.depends('start_date', 'end_date')
    def operation_uptime(self):
        if self.end_date and self.start_date:
            timedelta = fields.Datetime.from_string(self.end_date) - \
                fields.Datetime.from_string(self.start_date)
            self.uptime = timedelta.total_seconds() / 3600.
        else:
            self.uptime = 0
