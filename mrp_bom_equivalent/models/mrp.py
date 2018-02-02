# Copyright (C) 2017 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MRPBoMLine(models.Model):
    _inherit = 'mrp.bom.line'

    is_equivalences = fields.Boolean(
        string='Use equivalences'
    )
    equivalences_product_ids = fields.Many2many(
        "product.product",
        "mrp_bom_line_product_rel",
        "bom_line_id",
        "product_id",
        string="Non-Equivalent Products"
    )
