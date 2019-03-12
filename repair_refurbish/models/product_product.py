# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    refurbish_product_id = fields.Many2one(
        comodel_name='product.product', string='Refurbished Product',
        domain="[('type', '=', 'product')]")
