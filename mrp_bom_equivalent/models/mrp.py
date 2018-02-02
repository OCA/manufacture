# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MRPBoMLine(models.Model):
    _inherit = 'mrp.bom.line'

    use_equivalences = fields.Boolean(
        string='Use equivalences'
    )
    nonequivalent_product_ids = fields.Many2many(
        "product.product",
        "mrp_bom_line_product_rel",
        "bom_line_id",
        "product_id",
        string="Non-Equivalent Products"
    )
