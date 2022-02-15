# Copyright 2022 Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductionLot(models.Model):
    _inherit = "stock.production.lot"

    standard_price = fields.Float(
        string="Cost",
        company_dependent=True,
        digits="Product Price",
        groups="base.group_user",
        track_visibility="always",
    )
