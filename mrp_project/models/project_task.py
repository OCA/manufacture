# (c) 2014 Daniel Campos <danielcampos@avanzosc.es>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class Task(models.Model):
    _inherit = 'project.task'

    mrp_workorder_id = fields.Many2one(
        comodel_name='mrp.workorder',
        string='Work Order',
    )
    mrp_production_id = fields.Many2one(
        'mrp.production',
        string='Manufacturing Order'
    )
    # production_scheduled_products = fields.One2many(
    #   comodel_name="mrp.production.produce.line",
    #   inverse_name='task_id',
    #   related='mrp_production_id.product_lines',
    #   string='Scheduled Products'
    #   )
    final_product = fields.Many2one(
        comodel_name='product.product',
        string='Product to Produce',
        related='mrp_production_id.product_id'
    )

    @api.multi
    def name_get(self):
        if self.env.context.get('name_show_user'):
            res = []
            for task in self:
                res.append((
                    task.id, "[{0}] {1}".format(task.user_id.name, task.name)
                ))
            return res
        return super(Task, self).name_get()

    @api.multi
    def write(self, vals):
        for rec in self:
            super(Task, rec.with_context(
                production=rec.mrp_production_id
            )).write(vals)
        return True
