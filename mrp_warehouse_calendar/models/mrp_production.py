# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.depends("company_id", "date_planned_start", "is_planned", "product_id")
    def _compute_date_planned_finished(self):
        res = super(MrpProduction, self)._compute_date_planned_finished()
        productions = self.filtered(lambda p: p.date_planned_start and not p.is_planned)
        for production in productions:
            warehouse = self.picking_type_id.warehouse_id
            if warehouse.calendar_id:
                if production.product_id.produce_delay:
                    production.date_planned_finished = warehouse.calendar_id.plan_days(
                        +1 * production.product_id.produce_delay + 1,
                        production.date_planned_start,
                    )
                if production.company_id.manufacturing_lead:
                    production.date_planned_finished = warehouse.calendar_id.plan_days(
                        +1 * production.company_id.manufacturing_lead + 1,
                        production.date_planned_finished,
                    )
                production.move_finished_ids = [
                    (1, m.id, {"date": production.date_planned_finished})
                    for m in production.move_finished_ids
                ]
        return res

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        mo = super().copy(default=default)
        dt_planned = mo.date_planned_start
        warehouse = mo.picking_type_id.warehouse_id
        if warehouse.calendar_id and mo.product_id.produce_delay:
            date_expected = warehouse.calendar_id.plan_days(
                +1 * self.product_id.produce_delay + 1, dt_planned
            )
            mo.date_planned_finished = date_expected
        return mo
