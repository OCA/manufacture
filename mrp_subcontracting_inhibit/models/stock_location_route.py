# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockLocationRoute(models.Model):
    _inherit = "stock.location.route"

    subcontracting_inhibit = fields.Boolean(string="Inhibit subcontracting")
