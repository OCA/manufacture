# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_mrp_bom_version = fields.Boolean(
        string="Allow to re-edit BoMs",
        implied_group="mrp_bom_version.group_mrp_bom_version",
        help="The active state may be passed back to state draft",
    )
    bom_active_draft = fields.Boolean(
        string="Keep re-editing BoM active",
        help="This will allow you to define if those BoM passed back to draft"
        " are still activated or not",
    )

    def set_values(self):
        res = super().set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "mrp_bom_version.bom_active_draft", self.bom_active_draft
        )
        return res

    @api.model
    def get_values(self):
        res = super().get_values()
        bom_active_draft = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("mrp_bom_version.bom_active_draft", default=False)
        )
        res.update({"bom_active_draft": bom_active_draft})
        return res
