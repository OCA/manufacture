# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.depends(
        "company_id",
        "date_start",
        "is_planned",
        "product_id",
        "workorder_ids.duration_expected",
    )
    def _compute_date_finished(self):
        res = super()._compute_date_finished()
        productions = self.filtered(lambda p: p.date_start and not p.is_planned)
        for production in productions:
            warehouse = self.picking_type_id.warehouse_id
            if warehouse.calendar_id:
                if production.bom_id.produce_delay:
                    production.date_finished = warehouse.calendar_id.plan_days(
                        +1 * production.bom_id.produce_delay + 1,
                        production.date_start,
                    )
                if production.company_id.manufacturing_lead:
                    production.date_finished = warehouse.calendar_id.plan_days(
                        +1 * production.company_id.manufacturing_lead + 1,
                        production.date_finished,
                    )
                production.move_finished_ids = [
                    (1, m.id, {"date": production.date_finished})
                    for m in production.move_finished_ids
                ]
        return res

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        mo = super().copy(default=default)
        dt_planned = mo.date_start
        warehouse = mo.picking_type_id.warehouse_id
        if warehouse.calendar_id and mo.bom_id.produce_delay:
            date_expected = warehouse.calendar_id.plan_days(
                +1 * self.bom_id.produce_delay + 1, dt_planned
            )
            mo.date_finished = date_expected
        return mo
