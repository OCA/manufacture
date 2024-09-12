# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_component = fields.Boolean(
        compute="_compute_is_component_intermediate",
        store=True,
        help="Is component a product which has no BoM based on it +\
              is used in a BoM line",
    )
    is_intermediate = fields.Boolean(
        compute="_compute_is_component_intermediate",
        store=True,
        help="Is intermediate a product which has a BoM based on it +\
              is used in a BoM line",
    )

    @api.depends("bom_line_ids", "variant_bom_ids")
    def _compute_is_component_intermediate(self):
        for product in self:
            if product.bom_line_ids:
                # Difference is having a BoM with this product or not
                product.is_intermediate = True if product.bom_count else False
                product.is_component = not product.is_intermediate
            else:
                product.is_intermediate = False
                product.is_component = False
