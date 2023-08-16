# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_mrp_bom_version = fields.Boolean(
        string="Allow to re-edit BoMs",
        implied_group="mrp_bom_version.group_mrp_bom_version",
        help="The active state may be passed back to state draft.",
    )
    active_draft = fields.Boolean(
        string="Keep re-editing BoM active",
        help="This will allow you to define whether those BoM passed back to draft"
        " can still be re-activated or not.",
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            active_draft=self.env["ir.config_parameter"]
            .sudo()
            .get_param("active_draft", False)
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "active_draft", self.active_draft
        )
