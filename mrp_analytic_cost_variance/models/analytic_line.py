from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    workcenter_analytic_estimate_id = fields.Many2one(
        "mrp.workcenter.analytic.estimate"
    )
