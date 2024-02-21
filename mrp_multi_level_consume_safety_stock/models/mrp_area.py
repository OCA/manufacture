# Copyright 2023 Camptocamp  (https://www.camptocamp.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpArea(models.Model):
    _inherit = "mrp.area"

    safety_stock_target_date = fields.Date(
        string="Safety stock lead date",
        help="We will start rebuilding safety stock on that date",
        default=fields.Date.today,
    )
