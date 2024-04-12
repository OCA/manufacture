# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    workcenter_parent_level_empty = fields.Boolean(
        related="company_id.workcenter_parent_level_empty", store=True, readonly=False
    )
