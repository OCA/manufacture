# Copyright 2021 Le Filament
# License GPL-3.0 or later (https://www.gnu.org/licenses/gpl.html).

from odoo import fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    production_id = fields.Many2one(
        "mrp.production", "Production Order", check_company=True
    )
