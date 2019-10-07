# (c) 2014 Daniel Campos <danielcampos@avanzosc.es>
# (c) 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    @api.depends('analytic_account_id')
    def _compute_project_id(self):
        project = self.env['project.project']
        for record in self:
            project_domain = [(
                'analytic_account_id', '=', record.analytic_account_id.id
            )]
            record.project_id = project.search(project_domain, limit=1)[:1]

    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        compute=_compute_project_id,
        store=True,
        states={'draft': [('readonly', False)]}
    )

    @api.model
    def _prepare_project_vals(self, production):

        name = "{0} - {1} - {2}".format(
            production.product_id.name,
            fields.Date.today().year,
            production.name
        )
        return {
            'user_id': production.user_id.id,
            'name': name,
            #   'partner_id': production.origin.id, In this case it could
            #   be a function that gets the original Sale Order's and after
            #   return the partner's id from it.
        }

    @api.model
    def _prepare_production_task(self, workorder):
        stage_obj = self.env['project.task.type']
        stage = self.env.ref('project.project_stage_data_0')
        if not stage:
            stage = stage_obj.search([], order='sequence asc', limit=1)
        product = workorder.production_id.product_id
        task_name = "{0}::{1}- {2}".format(
            workorder.production_id.name,
            "[{0} {1}] ".format(
                workorder.name,
                product.default_code if product.default_code else ""
            ),
            product.name
        )
        task_descr = _("""
            <p><b>Manufacturing Order:</b> {0}</p>
            <p><b>Product to Produce:</b> [{1}]{2}</p>
            <p><b>Quantity to Produce:</b> {3}</p>
            <p><b>Bill of Material:</b> {4} - {5}</p>
            <p><b>Planned Date:</b> {6} - {7}</p>
            """.format(
            workorder.production_id.name,
            workorder.production_id.product_id and
            workorder.production_id.product_id.default_code or '',
            workorder.production_id.product_id.name,
            workorder.production_id.product_qty,
            workorder.production_id.bom_id.product_tmpl_id.name,
            workorder.production_id.bom_id.sequence,
            workorder.production_id.date_planned_start,
            workorder.production_id.date_planned_finished,
        ))
        return {
            'mrp_production_id': workorder.production_id.id,
            'mrp_workorder_id': workorder.id,
            'user_id': workorder.production_id.user_id.id,
            'reviewer_id': workorder.production_id.user_id.id,
            'name': task_name,
            'project_id': workorder.production_id.project_id.id,
            'stage_id': stage.id,
            'description': task_descr
        }

    @api.multi
    def _generate_workorders(self, exploded_boms):
        workorders = super(MrpProduction, self)._generate_workorders(
            exploded_boms
        )
        task_obj = self.env['project.task']
        for workorder in workorders:
            if not workorder.task_id:
                task_id = task_obj.create(self._prepare_production_task(workorder))
                workorder.write({
                    'task_id': task_id.id
                })
        return workorders

    @api.multi
    def action_create_project(self):
        project_obj = self.env['project.project']
        for production in self:
            if not production.project_id:
                project_vals = self._prepare_project_vals(production)
                project = project_obj.create(project_vals)
                production.write({
                    'project_id': project.id
                })
        return True

    @api.multi
    def unlink(self):
        projects = self.mapped('project_id').filtered('automatic_creation')
        tasks = self.env['project.task'].search(
            [('project_id', 'in', projects.ids)]
        )
        # if not tasks.mapped('work_ids'):
        child_tasks = tasks.filtered(lambda x: x.parent_ids)
        child_tasks.unlink()
        (tasks - child_tasks).unlink()
        projects.unlink()

        return super(MrpProduction, self).unlink()
