# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    mrp_procurement_no_autoconfirm = fields.Boolean(
        related="company_id.mrp_procurement_no_autoconfirm",
        string="Do Not Auto-Confirm MOs Created From Another MO",
        readonly=False,
    )
