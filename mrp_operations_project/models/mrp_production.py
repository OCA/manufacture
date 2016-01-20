# -*- coding: utf-8 -*-
# (c) 2014 Daniel Campos <danielcampos@avanzosc.es>
# (c) 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models, _


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    @api.multi
    def _compute_task_m2m(self):
        for record in self:
            record.task_m2m = record.task_ids

    # needed because the one2many can't be part of a domain directly
    task_m2m = fields.Many2many(
        comodel_name="project.task", compute="_compute_task_m2m")

    @api.model
    def _prepare_workorder_task(self, workorder):
        task_domain = [
            ('mrp_production_id', '=', workorder.production_id.id),
            ('workorder', '=', False)]
        production_tasks = self.env['project.task'].search(task_domain)
        task_descr = _("""
        Manufacturing Order: %s
        Work Order: %s
        Workcenter: %s
        Cycle: %s
        Hour: %s
        """) % (workorder.production_id.name, workorder.name,
                workorder.workcenter_id.name, workorder.cycle,
                workorder.hour)
        return {
            'mrp_production_id': workorder.production_id.id,
            'workorder': workorder.id,
            'reviewer_id': workorder.production_id.user_id.id,
            'description': task_descr,
            'project_id': workorder.production_id.project_id.id,
            'parent_ids': [(6, 0, production_tasks.ids)]
        }

    @api.model
    def _prepare_tasks_vals(self, workorder, task_vals):
        """Method to be inheritable for having the possibility of creating
        multiple tasks from one work order.
        :param workorder: Work order
        :param task_vals: Template task values
        :return: List of dictionaries with each of the task values to create.
        """
        tasks_vals = []
        wk_operation = workorder.routing_wc_line.op_wc_lines.filtered(
            lambda r: r.workcenter == workorder.workcenter_id)[:1]
        count = (wk_operation.op_number or
                 workorder.workcenter_id.op_number)
        op_list = workorder.workcenter_id.operators
        for i in range(count):
            # Create a task for each employee
            if len(op_list) > i:
                task_vals['user_id'] = op_list[i].id
            task_name = (_("%s:: WO%s-%s:: %s") %
                         (workorder.production_id.name,
                          str(workorder.sequence).zfill(3),
                          str(i).zfill(3), workorder.name))
            task_vals['name'] = task_name
            tasks_vals.append(task_vals.copy())
        return tasks_vals

    @api.multi
    def action_start_working(self):
        res = super(MrpProductionWorkcenterLine, self).action_start_working()
        task_obj = self.env['project.task']
        for workorder in self:
            task_vals = self._prepare_workorder_task(workorder)
            tasks_vals = self._prepare_tasks_vals(workorder, task_vals)
            for task_vals in tasks_vals:
                task_obj.create(task_vals)
        return res
