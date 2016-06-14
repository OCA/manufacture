# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
