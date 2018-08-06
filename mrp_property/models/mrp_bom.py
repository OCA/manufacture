# coding: utf-8
# Copyright 2008 - 2016 Odoo S.A.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, models, fields


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    property_ids = fields.Many2many(
        'mrp.property',
        'mrp_bom_mrp_property_rel',
        'mrp_bom_id', 'mrp_property_id',
        string='Properties',
        help=("If a production product is manufactured for a sale order, the "
              "BoM that has the same properties as the sale order line will "
              "be selected (a BoM with no properties at all could be selected "
              "as a fallback."))

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """ If limit is set to 1 and property_ids is set in the context, search
        a BoM which has all properties specified, or if you can not find one,
        you return a BoM without any properties with the lowest sequence. """
        check_properties = False
        if limit == 1 and self.env.context.get('property_ids'):
            check_properties = True
            limit = None
        boms = super(MrpBom, self).search(
            args, offset=offset, limit=limit, order=order, count=count)
        if check_properties:
            bom_empty_prop = self.env['mrp.bom']
            property_ids = set(self.env.context['property_ids'])
            for bom in boms:
                if bom.property_ids:
                    if not set(bom.property_ids.ids) - property_ids:
                        return bom
                elif not bom_empty_prop:
                    bom_empty_prop = bom
            return bom_empty_prop
        return boms

    @api.model
    def _bom_find(self, product_tmpl=None, product=None, picking_type=None,
                  company_id=False):
        """ If property_ids are set in the context at this point, add an
        additional value in the context that triggers the filter on these
        properties in this model's search method """
        if self.env.context.get('property_ids'):
            self = self.with_context(check_properties=True)
        return super(MrpBom, self)._bom_find(
            product_tmpl=product_tmpl, product=product,
            picking_type=picking_type, company_id=company_id)
