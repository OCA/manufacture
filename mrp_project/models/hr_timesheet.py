# (c) 2014 Daniel Campos <danielcampos@avanzosc.es>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    mrp_production_id = fields.Many2one(
        comodel_name='mrp.production',
        string='Manufacturing Order'
    )
    mrp_workorder_id = fields.Many2one(
        comodel_name='mrp.workorder',
        string='Work Order'
    )

    @api.model
    def create(self, vals):
        context = dict(self.env.context)
        production = context.get('production', False)
        workorder = context.get('workorder', False)
        vals['mrp_production_id'] = vals.get(
            'mrp_production_id', False
        ) or production and production.id
        vals['workorder'] = vals.get(
            'workorder', False
        ) or workorder and workorder.id
        return super(AccountAnalyticLine, self).create(vals)
