# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import Counter
from openerp import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    bom_count = fields.Integer(compute='_compute_bom_count')

    dismantling_bom_count = fields.Integer(
        compute='_compute_dismantling_bom_count'
    )

    @api.multi
    def _compute_bom_count(self):
        """ Compute the number of BOM for these products (except dismantling).
        """
        for product in self:
            product.bom_count = self.env['mrp.bom'].search_count(
                product.get_bom_domain()
            )

    @api.multi
    def _compute_dismantling_bom_count(self):
        """ Compute the number of dismantling BOM for these products.
        """
        for product in self:
            product.dismantling_bom_count = self.env['mrp.bom'].search_count(
                product.get_dismantling_bom_domain()
            )

    @api.multi
    def action_view_bom(self):
        """ Override parent method to add a domain which filter out
        dismantling BoM
        """
        result = super(ProductProduct, self).action_view_bom()
        result['domain'] = self.get_bom_domain()
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

    @api.multi
    def action_view_dismantling_bom(self):
        """ Return the dismantling BOM tree view act window which is filtered
        for these products.
        """
        self.ensure_one()

        action = self.env['ir.actions.act_window'].for_xml_id(
            'mrp_bom_dismantling', 'mrp_bom_dismantling_form_action'
        )

        action['domain'] = self.get_dismantling_bom_domain()

        return action

    def get_bom_domain(self):
        """ Return the domain to apply for searching BOM for this product.

        :type: list
        """
        self.ensure_one()
        return [
            '&',
            ('dismantling', '=', False),
            '|',
            ('product_id', '=', self.id),
            '&',
            ('product_id', '=', False),
            ('product_tmpl_id', '=', self.product_tmpl_id.id),
        ]

    def get_dismantling_bom_domain(self):
        """ Return the domain to apply for searching dismantling BOM
        for this product.

        :type: list
        """
        return [
            ('dismantling', '=', True),
            ('dismantled_product_id', '=', self.id),
        ]
