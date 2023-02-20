# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.onchange("bom_id")
    def _onchange_bom_id(self):
        super()._onchange_bom_id()
        if self.bom_id and self.bom_id.user_id:
            self.user_id = self.bom_id.user_id
