# Copyright (C) 2023 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _reconcile_interim_accounts(self):
        self.ensure_one()
        for account in self.account_move_line_ids.mapped("account_id").filtered(
            lambda x: x.reconcile
        ):
            mls = self.account_move_line_ids.filtered(
                lambda x: x.account_id == account and not x.reconciled
            )
            mls.reconcile()

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        for order in self:
            order._reconcile_interim_accounts()
        return res
