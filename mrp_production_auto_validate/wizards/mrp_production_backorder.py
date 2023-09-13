# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class MrpProductionBackorder(models.TransientModel):
    _inherit = "mrp.production.backorder"

    def action_backorder(self):
        # Bypass the 'auto_validate' constraint regarding qty to produce
        # when creating a backorder.
        self = self.with_context(disable_check_mo_auto_validate=True)
        return super().action_backorder()
