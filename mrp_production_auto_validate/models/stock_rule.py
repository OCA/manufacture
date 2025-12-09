# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _run_manufacture(self, procurements):
        return super(
            StockRule, self.with_context(_split_create_values_for_auto_validation=True)
        )._run_manufacture(procurements)

    def _make_mo_get_domain(self, procurements, bom):
        # Make sure a procurement will not try to add on existing mo
        if bom.mo_auto_validation:
            return [("id", "=", -1)]
        return super()._make_mo_get_domain(procurements, bom)
