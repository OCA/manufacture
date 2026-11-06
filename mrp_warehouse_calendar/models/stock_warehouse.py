# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import UTC

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    def _mrp_calendar_plan_days(self, days, date_from):
        """Plan ``days`` working days on the warehouse calendar.

        In 20.0, ``resource.calendar.plan_days()`` converts the reference
        date to the company timezone with ``astimezone()``, so a naive
        datetime would be interpreted as server local time. Localize the
        (naive UTC) Odoo datetime explicitly and return a naive UTC datetime.
        """
        self.ensure_one()
        date_from = fields.Datetime.to_datetime(date_from)
        res = self.calendar_id.plan_days(days, date_from.replace(tzinfo=UTC))
        return res and res.astimezone(UTC).replace(tzinfo=None)
