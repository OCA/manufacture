# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    workcenter_productivity_id = fields.Many2one(
        "mrp.workcenter.productivity",
        string="Manufacturing Time Log",
    )
