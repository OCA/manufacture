# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    qc_triggers = fields.One2many(
        comodel_name="qc.trigger.product_line", inverse_name="product",
        string="Quality control triggers")
