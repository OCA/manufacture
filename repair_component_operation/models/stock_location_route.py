# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class StockLocationRoute(models.Model):
    _inherit = "stock.location.route"

    repair_component_selectable = fields.Boolean(
        string="Selectable on Repair Components"
    )
