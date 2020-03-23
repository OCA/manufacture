# Copyright 2019-20 ForgeFlow S.L. (http://www.forgeflow.com)
# - Lois Rilo <lois.rilo@forgeflow.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.tools.float_utils import float_round

logger = logging.getLogger(__name__)


class MultiLevelMrp(models.TransientModel):
    _inherit = "mrp.multi.level"

    @api.model
    def _prepare_mrp_move_data_from_estimate(self, estimate, product_mrp_area, date):
        mrp_type = "d"
        origin = "fc"
        daily_qty = float_round(
            estimate.daily_qty,
            precision_rounding=product_mrp_area.product_id.uom_id.rounding,
            rounding_method="HALF-UP",
        )
        return {
            "mrp_area_id": product_mrp_area.mrp_area_id.id,
            "product_id": product_mrp_area.product_id.id,
            "product_mrp_area_id": product_mrp_area.id,
            "production_id": None,
            "purchase_order_id": None,
            "purchase_line_id": None,
            "stock_move_id": None,
            "mrp_qty": -daily_qty * product_mrp_area.group_estimate_days,
            "current_qty": -daily_qty,
            "mrp_date": date,
            "current_date": date,
            "mrp_type": mrp_type,
            "mrp_origin": origin,
            "mrp_order_number": None,
            "parent_product_id": None,
            "name": "Forecast",
            "state": "confirmed",
        }

    @api.model
    def _estimates_domain(self, product_mrp_area):
        locations = product_mrp_area.mrp_area_id._get_locations()
        return [
            ("product_id", "=", product_mrp_area.product_id.id),
            ("location_id", "in", locations.ids),
            ("date_to", ">=", fields.Date.today()),
        ]

    @api.model
    def _init_mrp_move_from_forecast(self, product_mrp_area):
        res = super(MultiLevelMrp, self)._init_mrp_move_from_forecast(product_mrp_area)
        if not product_mrp_area.group_estimate_days:
            return False
        today = fields.Date.today()
        domain = self._estimates_domain(product_mrp_area)
        estimates = self.env["stock.demand.estimate"].search(domain)
        for rec in estimates:
            start = rec.date_range_id.date_start
            if start < today:
                start = today
            mrp_date = fields.Date.from_string(start)
            date_end = fields.Date.from_string(rec.date_range_id.date_end)
            delta = timedelta(days=product_mrp_area.group_estimate_days)
            while mrp_date <= date_end:
                mrp_move_data = self._prepare_mrp_move_data_from_estimate(
                    rec, product_mrp_area, mrp_date
                )
                self.env["mrp.move"].create(mrp_move_data)
                mrp_date += delta
        return res
