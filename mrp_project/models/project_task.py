# -*- coding: utf-8 -*-
# (c) 2014 Daniel Campos <danielcampos@avanzosc.es>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    workorder = fields.Many2one(
        comodel_name='mrp.production.workcenter.line', string='Work Order',
        oldname='wk_order')
    mrp_production_id = fields.Many2one(
        'mrp.production', string='Manufacturing Order')
    production_scheduled_products = fields.One2many(
        comodel_name="mrp.production.product.line", inverse_name='task_id',
        related='mrp_production_id.product_lines', string='Scheduled Products')
    final_product = fields.Many2one(
        comodel_name='product.product', string='Product to Produce',
        store=False, related='mrp_production_id.product_id')

    @api.multi
    def name_get(self):
        if self.env.context.get('name_show_user'):
            res = []
            for task in self:
                res.append(
                    (task.id, "[%s] %s" % (task.user_id.name, task.name)))
            return res
        return super(ProjectTask, self).name_get()

    @api.multi
    def write(self, vals):
        for rec in self:
            super(ProjectTask, rec.with_context(
                production=rec.mrp_production_id)).write(vals)
        return True
