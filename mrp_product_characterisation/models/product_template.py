# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_component = fields.Boolean(
        related="product_variant_ids.is_component",
    )

    is_intermediate = fields.Boolean(
        related="product_variant_ids.is_intermediate",
    )
