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

    def _should_auto_confirm_procurement_mo(self, p):
        if p.state != "draft":
            return False
        if len(p.move_dest_ids) > 1:
            return (not p.orderpoint_id and p.move_raw_ids) or (
                all(m.procure_method != "make_to_order" for m in p.move_dest_ids)
                and not p.move_raw_ids
                and not p.workorder_ids
            )
        return super()._should_auto_confirm_procurement_mo(p)
