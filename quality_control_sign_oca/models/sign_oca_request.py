# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class SignOcaRequest(models.Model):
    _inherit = "sign.oca.request"

    inspection_id = fields.Many2one("qc.inspection", string="Inspection")
