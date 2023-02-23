# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class MrpComponentOperate(models.Model):
    _inherit = "mrp.component.operate"

    scrap_reason_code_id = fields.Many2one(
        "scrap.reason.code",
        string="Scrap Reason Code",
    )

    def _create_scrap(self):
        scrap = super()._create_scrap()
        scrap.reason_code_id = self.scrap_reason_code_id
        return scrap
