# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api
from datetime import datetime


class ProjectTaskWork(models.Model):
    _inherit = 'project.task.work'

    workorder = fields.Many2one(
        comodel_name="mrp.production.workcenter.line",
        related="task_id.workorder", store=True, string="Work order")

    @api.multi
    def button_end_work(self):
        end_date = datetime.now()
        for work in self:
            date = fields.Datetime.from_string(work.date)
            work.hours = (end_date - date).total_seconds() / 3600
        return True

    @api.multi
    def onchange_task_id(self, task_id):
        res = {}
        if task_id:
            task = self.env['project.task'].browse(task_id)
            res['value'] = {'user_id': task.user_id.id}
        return res
