# Copyright (C) 2021, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    bom_cost_email = fields.Char(
        string="BoM cost rollup email",
        related="company_id.bom_cost_email",
        readonly=False,
        help="BoM Cost rollup Email notification will be sent to this email address",
    )
