# Copyright (C) 2021, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    bom_cost_email = fields.Char(
        string="BoM cost rollup email",
        help="BoM Cost rollup Email notification will be sent to this email address",
    )
