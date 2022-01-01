#  Copyright 2022 Simone Rubino - Takobi
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpProductProduceLine (models.TransientModel):
    _inherit = "mrp.product.produce.line"

    production_src_location_id = fields.Many2one(
        string="Production source location",
        related='product_produce_id.production_id.location_src_id',
        readonly=True,
    )
