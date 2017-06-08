# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    machine_ok = fields.Boolean('Can be a Machine', help="Determines if the "
                                "product is related with a machine.")
