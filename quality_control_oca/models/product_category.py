# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ProductCategory(models.Model):
    _inherit = "product.category"

    qc_triggers = fields.One2many(
        comodel_name="qc.trigger.product_category_line",
        inverse_name="product_category",
        string="Quality control triggers")
