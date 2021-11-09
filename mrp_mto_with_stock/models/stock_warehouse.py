# Copyright 2017 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    mrp_mto_mts_forecast_qty = fields.Boolean(
        string="MRP MTO with forecast stock",
        help="When you use Mrp_mto_with_stock, the procurement creation is "
             "based on reservable stock by default. Check this option if "
             "you prefer base it on the forecast stock. In this case, the "
             "created procurements won't be linked to the raw material moves")
