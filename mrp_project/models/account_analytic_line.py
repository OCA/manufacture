# -*- coding: utf-8 -*-
# (c) 2014 Daniel Campos <danielcampos@avanzosc.es>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    mrp_production_id = fields.Many2one(
        comodel_name='mrp.production', string='Manufacturing Order')
    workorder = fields.Many2one(
        comodel_name='mrp.production.workcenter.line', string='Work Order')
    task_id = fields.Many2one('project.task', 'Project Task')
