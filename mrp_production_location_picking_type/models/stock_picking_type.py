# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    production_location_id = fields.Many2one(
        "stock.location",
        string="Production Location",
        help="Default production location for manufacturing operations "
        "using this operation type.",
        domain="[('usage', '=', 'production'), ('company_id', 'in', [company_id, False])]",
    )
