# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_date_planned(self, product_id, company_id, values):
        date_planned = super()._get_date_planned(product_id, company_id, values)
        picking_type = self.picking_type_id or values["warehouse_id"].manu_type_id
        # We force the date planned to be at the beginning of the day.
        # So no work intervals are found in planned date.
        dt_planned = fields.Datetime.to_datetime(values["date_planned"]).replace(hour=0)
        warehouse = picking_type.warehouse_id
        if warehouse.calendar_id and product_id.produce_delay:
            lead_days = (
                values["company_id"].manufacturing_lead + product_id.produce_delay
            )
            date_expected = warehouse.calendar_id.plan_days(-1 * lead_days, dt_planned)
            date_planned = date_expected
        return date_planned
