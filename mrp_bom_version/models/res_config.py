# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class MrpConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_mrp_bom_version = fields.Boolean(
        string="Allow to re-edit BoMs",
        implied_group="mrp_bom_version.group_mrp_bom_version",
        help="The active state may be passed back to state draft",
    )
    active_draft = fields.Boolean(
        string="Keep re-editing BoM active",
        help="This will allow you to define if those BoM passed back to draft"
        " are still activated or not",
        config_parameter="mrp_bom_version.active_draft",
    )
