# Copyright (C) 2019 Akretion (http://www.akretion.com). All Rights Reserved
# @author David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allow_unbuild_purchased = fields.Boolean(
        help="If checked, unbuild orders doesn't assume a previous "
        "manufacturing order have built this product.\n"
        "In this case it's a purchased product and you want unbuild it"
    )
