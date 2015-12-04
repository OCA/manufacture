# -*- coding: utf-8 -*-
# (c) 2014 Daniel Campos (danielcampos@avanzosc.es)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    workorder_scheduled_products = fields.One2many(
        comodel_name="mrp.production.product.line", inverse_name='task_id',
        related='workorder.product_line', store=False,
        string='Scheduled Products')
