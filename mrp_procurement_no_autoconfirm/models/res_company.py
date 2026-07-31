# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    mrp_procurement_no_autoconfirm = fields.Boolean(default=True)
