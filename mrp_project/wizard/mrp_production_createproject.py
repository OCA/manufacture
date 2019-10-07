# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MrpProductionCreateProject(models.TransientModel):
    """ wizard to create a Project from a Manufacturing Order """
    _name = "mrp.production.createproject"

    @api.model
    def default_get(self, fields):
        result = super(MrpProductionCreateProject, self).default_get(fields)
        mrp_production_id = self.env.context.get('active_id')
        if mrp_production_id:
            result['mrp_production_id'] = mrp_production_id
        return result

    mrp_production_id = fields.Many2one(
        'mrp.production',
        string='Production',
        domain=[('type', '=', 'production')]
    )
    project_id = fields.Many2one(
        'project.project',
        help=_("Leave it blank if you want create a new project with"
               "the manufacturing order's name as default name.")
    )

    @api.multi
    def action_create_project_task(self):
        self.ensure_one()
        # get the production to update
        production = self.mrp_production_id
        project = self.project_id

        # If this production come from a sale order and that order
        # has an analytic account assigned, then project is child of
        # that analytic account

        obj_production = self.env['mrp.production']
        obj_order = self.env['sale.order']

        if not project.id and not production.project_id:
            if 'sale_order_id' in obj_production._fields and \
                    'related_project_id' in obj_order._fields:
                sale_order = production.sale_order_id
                if sale_order:
                    project = sale_order.related_project_id
                    if project.id:
                        production.write({
                            'analytic_account_id':
                                project.analytic_account_id.id
                        })
                    else:
                        production.action_create_project()
                else:
                    production.action_create_project()
            else:
                production.action_create_project()
        elif project.id and not production.project_id:
            production.write({
                'project_id': project.id
            })
        else:
            raise UserError(_(
                '''This manufacturing order already has a related project.
                    Order: {0}, Project: {1}'''.format(
                    production,
                    production.project_id
                )
            ))

        return True
