# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    repair_id = fields.Many2one("repair.order", readonly=1)
