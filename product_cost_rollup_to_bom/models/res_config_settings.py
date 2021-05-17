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

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            bom_cost_email=self.env["ir.config_parameter"]
            .sudo()
            .get_param("product_cost_rollup_to_bom.bom_cost_email")
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "product_cost_rollup_to_bom.bom_cost_email", self.bom_cost_email
        )


class ResCompany(models.Model):
    _inherit = "res.company"

    bom_cost_email = fields.Char(
        string="BoM cost rollup email",
        help="BoM Cost rollup Email notification will be sent to this email address",
    )
