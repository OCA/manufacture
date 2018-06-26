# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if 'nonequivalent_product_id' in self._context:
            category_id = self.browse(
                self._context.get('nonequivalent_product_id')).categ_id
            recs = self.search(
                [('categ_id', 'child_of', category_id.id),
                 ('id', '!=', self._context.get('nonequivalent_product_id')),
                 ('name', operator, name)] + args, limit=limit)
            if not recs:
                recs = self.browse()
            return recs.name_get()
        return super(ProductProduct, self).name_search(name, args=args,
                                                       operator=operator,
                                                       limit=limit)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None,
                    order=None):
        if 'nonequivalent_product_id' in self._context:
            category_id = self.browse(
                self._context.get('nonequivalent_product_id')).categ_id
            domain +=\
                [('categ_id', 'child_of', category_id.id),
                 ('id', '!=', self._context.get('nonequivalent_product_id'))]
        order = order or self.product_tmpl_id.priority
        return super(ProductProduct, self).search_read(domain=domain,
                                                       fields=fields,
                                                       offset=offset,
                                                       limit=limit,
                                                       order=order)
