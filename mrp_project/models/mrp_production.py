# -*- coding: utf-8 -*-
# (c) 2014 Daniel Campos <danielcampos@avanzosc.es>
# (c) 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    project_id = fields.Many2one(
        comodel_name="project.project", string="Project", copy=False,
        readonly=True, states={'draft': [('readonly', False)]})
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account", string="Analytic Account",
        related="project_id.analytic_account_id", store=True)

    @api.model
    def _prepare_production_task(self, production):
        product = production.product_id
        if product.default_code:
            task_name = "%s::[%s] %s" % (
                production.name, product.default_code, product.name)
        else:
            task_name = "%s::%s" % (production.name, product.name)
        task_descr = _("""
        Manufacturing Order: %s
        Product to Produce: [%s]%s
        Quantity to Produce: %s
        Bill of Material: %s
        Planned Date: %s
        """) % (production.name, production.product_id.default_code,
                production.product_id.name, production.product_qty,
                production.bom_id.name, production.date_planned)
        return {
            'mrp_production_id': production.id,
            'user_id': production.user_id.id,
            'reviewer_id': production.user_id.id,
            'name': task_name,
            'project_id': production.project_id.id,
            'description': task_descr
        }

    @api.multi
    def action_in_production(self):
        task_obj = self.env['project.task']
        for record in self:
            task_domain = [('mrp_production_id', '=', record.id),
                           ('workorder', '=', False)]
            tasks = task_obj.search(task_domain)
            if not tasks:
                task_obj.create(self._prepare_production_task(record))
        return super(MrpProduction, self).action_in_production()

    @api.multi
    def action_confirm(self):
        procurement_obj = self.env['procurement.order']
        project_obj = self.env['project.project']
        mto_record = self.env.ref('stock.route_warehouse0_mto')
        result = super(MrpProduction, self).action_confirm()
        for record in self:
            if not record.project_id:
                project_vals = {
                    'name': record.name,
                    'use_tasks': True,
                    'automatic_creation': True,
                }
                project = project_obj.create(project_vals)
                record.project_id = project.id
            # Refresh MTO procurement data
            main_project = record.project_id.id
            for move in record.move_lines:
                if mto_record in move.product_id.route_ids:
                    move.main_project_id = main_project
                    procurements = procurement_obj.search(
                        [('move_dest_id', '=', move.id)])
                    procurements.write({'main_project_id': main_project})
                    procurements.refresh()
                    procurements.set_main_project()
        return result

    @api.multi
    def unlink(self):
        projects = self.mapped('project_id').filtered('automatic_creation')
        tasks = self.env['project.task'].search(
            [('project_id', 'in', projects.ids)])
        if not tasks.mapped('work_ids'):
            child_tasks = tasks.filtered(lambda x: x.parent_ids)
            child_tasks.unlink()
            (tasks - child_tasks).unlink()
            projects.unlink()
        return super(MrpProduction, self).unlink()


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    @api.multi
    def _compute_task_m2m(self):
        for record in self:
            record.task_m2m = record.task_ids

    task_ids = fields.One2many(
        comodel_name="project.task", inverse_name="workorder", string="Tasks")
    # needed because the one2many can't be part of a domain directly
    task_m2m = fields.Many2many(
        comodel_name="project.task", compute="_compute_task_m2m")
    work_ids = fields.One2many(
        comodel_name="project.task.work", inverse_name="workorder",
        string="Task works")

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
        task_vals['name'] = (
            _("%s:: WO%s:: %s") %
            (workorder.production_id.name, str(workorder.sequence).zfill(3),
             workorder.name))
        return [task_vals]

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
