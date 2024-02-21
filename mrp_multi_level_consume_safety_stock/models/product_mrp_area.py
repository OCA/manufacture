# Copyright 2023 Camptocamp  (https://www.camptocamp.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ProductMrpArea(models.Model):
    _inherit = "product.mrp.area"

    safety_stock_target_date = fields.Date(
        string="Safety stock lead date",
        compute="_compute_safety_stock_target_date",
        help="The date when we can restart supplying for this product",
    )

    @api.depends(
        "mrp_lead_time",
        "mrp_area_id.safety_stock_target_date",
    )
    def _compute_safety_stock_target_date(self):
        today = fields.Date.context_today(self)
        for rec in self:
            delta = relativedelta(days=rec.mrp_lead_time)
            area_target_date = rec.mrp_area_id.safety_stock_target_date or today
            rec.safety_stock_target_date = max(today, area_target_date + delta)
