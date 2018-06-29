# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.onchange('date_planned_start', 'product_id')
    def onchange_date_planned(self):
        dt_planned = fields.Datetime.from_string(self.date_planned_start)
        warehouse = self.picking_type_id.warehouse_id
        if warehouse.calendar_id and self.product_id.produce_delay:
            date_expected_finished = warehouse.calendar_id.plan_days(
                +1 * self.product_id.produce_delay + 1, dt_planned)
            self.date_planned_finished = date_expected_finished

    @api.multi
    def copy(self, default=None):
        mo = super(MrpProduction, self).copy(default=default)
        dt_planned = fields.Datetime.from_string(mo.date_planned_start)
        warehouse = mo.picking_type_id.warehouse_id
        if warehouse.calendar_id and mo.product_id.produce_delay:
            date_expected = warehouse.calendar_id.plan_days(
                +1 * self.product_id.produce_delay + 1, dt_planned)
            mo.date_planned_finished = date_expected
        return mo
