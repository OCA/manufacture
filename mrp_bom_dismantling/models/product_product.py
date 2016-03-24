# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def action_view_bom(self, cr, uid, ids, context=None):
        """ Override parent method to add a domain which filter out
        dismantling BoM
        """
        result = super(ProductProduct, self).action_view_bom(
            cr, uid, ids, context
        )
        result['domain'] = [('dismantling', '=', False)]
        return result
