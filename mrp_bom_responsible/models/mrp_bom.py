# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    user_id = fields.Many2one(
        "res.users", "Responsible", default=lambda self: self._uid
    )
