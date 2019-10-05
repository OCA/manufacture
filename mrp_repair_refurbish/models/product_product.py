# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    refurbish_product_id = fields.Many2one(
        comodel_name='product.product', string='Refurbished Product',
        domain="[('type', '=', 'product')]")
