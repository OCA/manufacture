# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    purchase_order_id = fields.Many2one(
        "purchase.order", "Subcontract Purchase Order", readonly=True
    )
