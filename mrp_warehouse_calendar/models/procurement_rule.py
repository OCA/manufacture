# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _get_date_planned(self, product_id, values):
        date_planned = super(ProcurementRule, self)._get_date_planned(
            product_id, values)
        picking_type = self.picking_type_id or \
            values['warehouse_id'].manu_type_id
        dt_planned = fields.Datetime.from_string(values['date_planned'])
        warehouse = picking_type.warehouse_id
        if warehouse.calendar_id and product_id.produce_delay:
            lead_days = values['company_id'].manufacturing_lead + \
                product_id.produce_delay
            date_expected = warehouse.calendar_id.plan_days(
                -1 * lead_days - 1, dt_planned)
            date_planned = date_expected
        return date_planned
