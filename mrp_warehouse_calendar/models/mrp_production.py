# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.onchange("date_planned_start", "product_id")
    def _onchange_date_planned_start(self):
        res = super(MrpProduction, self)._onchange_date_planned_start()
        if self.date_planned_start and not self.is_planned:
            warehouse = self.picking_type_id.warehouse_id
            if warehouse.calendar_id:
                if self.product_id.produce_delay:
                    self.date_planned_finished = warehouse.calendar_id.plan_days(
                        +1 * self.product_id.produce_delay + 1, self.date_planned_start
                    )
                if self.company_id.manufacturing_lead:
                    self.date_planned_finished = warehouse.calendar_id.plan_days(
                        +1 * self.company_id.manufacturing_lead + 1,
                        self.date_planned_finished,
                    )
                self.move_finished_ids = [
                    (1, m.id, {"date": self.date_planned_finished})
                    for m in self.move_finished_ids
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
