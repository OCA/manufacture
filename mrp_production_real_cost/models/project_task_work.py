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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, api


class ProjectTaskWork(models.Model):

    _inherit = 'project.task.work'

    @api.model
    def create(self, vals):
        result = super(ProjectTaskWork, self).create(vals)
        if result.hr_analytic_timesheet_id and result.task_id:
            analytic_line = result.hr_analytic_timesheet_id.line_id
            task = result.task_id
            if task.mrp_production_id or task.wk_order:
                analytic_line.write({'mrp_production_id':
                                     task.mrp_production_id.id,
                                     'workorder': task.wk_order.id})
        return result

    @api.model
    def write(self, vals):
        result = super(ProjectTaskWork, self).write(vals)
        if 'hr_analytic_timesheet_id' in vals or 'task_id' in vals:
            analytic_line = self.hr_analytic_timesheet_id.line_id
            task = self.task_id
            if task.mrp_production_id or task.wk_order:
                analytic_line.write({'mrp_production_id':
                                     task.mrp_production_id.id,
                                     'workorder': task.wk_order.id})
        return result
