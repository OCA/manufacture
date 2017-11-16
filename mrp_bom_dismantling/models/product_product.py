# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import Counter
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

    def _get_component_needs(self, product, bom):
        """ Return the needed qty of each compoments in the *bom* of *product*.

        :type product: product_product
        :type bom: mrp_bom
        :rtype: collections.Counter
        """
        bom_obj = self.env['mrp.bom']
        uom_obj = self.env['product.uom']
        product_obj = self.env['product.product']
        needs = Counter()
        for bom_component in bom_obj._bom_explode(bom, product, 1.0)[0]:
            product_uom = uom_obj.browse(bom_component['product_uom'])
            component = product_obj.browse(bom_component['product_id'])

            component_qty = uom_obj._compute_qty_obj(
                product_uom,
                bom_component['product_qty'],
                component.uom_id,
            )
            needs += Counter(
                {component: component_qty}
            )
        return needs
