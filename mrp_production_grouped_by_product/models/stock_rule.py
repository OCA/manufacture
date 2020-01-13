# Copyright 2018 Tecnativa - David Vidal
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _run_manufacture(self, procurements):
        return super(
            StockRule, self.with_context(group_mo_by_product=True)
        )._run_manufacture(procurements)
