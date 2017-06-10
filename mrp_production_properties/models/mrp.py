# -*- coding: utf-8 -*-
# Copyright 2014 <alex.comba@agilebg.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields


class MrpPropertyGroup(models.Model):
    """
    Group of mrp properties.
    """
    _name = 'mrp.property.group'
    _description = 'Property Group'

    name = fields.Char('Property Group', required=True)
    description = fields.Text('Description')


class MrpProperty(models.Model):
    """
    Properties of mrp.
    """
    _name = 'mrp.property'
    _description = 'Property'

    name = fields.Char('Name', required=True)
    composition = fields.Selection([('min', 'min'), ('max', 'max'),
                                    ('plus', 'plus')],
                                   'Properties composition', required=True,
                                   help="Not used in computations, "
                                        "for information purpose only.",
                                   default='min')
    group_id = fields.Many2one('mrp.property.group', 'Property Group',
                               required=True)
    description = fields.Text('Description')


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    property_ids = fields.Many2many('mrp.property',
                                    'mrp_bom_property_rel',
                                    'bom_id', 'property_id',
                                    string='Properties')

    @api.model
    def _bom_find(self, product_tmpl=None, product=None, picking_type=None,
                  company_id=False):
        property_ids = self._context.get('property_ids')
        if property_ids:
            if product:
                if not product_tmpl:
                    product_tmpl = product.product_tmpl_id
                domain = ['|', ('product_id', '=', product.id), '&',
                          ('product_id', '=', False),
                          ('product_tmpl_id', '=', product_tmpl.id)]
            elif product_tmpl:
                domain = [('product_tmpl_id', '=', product_tmpl.id)]
            else:
                # neither product nor template, makes no sense to search
                return False
            if picking_type:
                domain += ['|', ('picking_type_id', '=', picking_type.id),
                           ('picking_type_id', '=', False)]
            if company_id or self.env.context.get('company_id'):
                domain += [('company_id', '=', company_id or
                            self.env.context.get('company_id'))]

            bom_ids = self.search(domain, order='sequence, product_id')
            for bom in bom_ids.sorted(key=lambda p:
            (p.sequence, p.product_id)):
                for ctx_p in property_ids:
                    if ctx_p in [p.id for p in bom.property_ids]:
                        return bom
            # Not found BoM with property from procurement return first BoM
            if bom_ids:
                return bom_ids[0]
        else:
            return super(MrpBom, self)._bom_find(product_tmpl, product,
                                                 picking_type, company_id)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    property_ids = fields.Many2many('mrp.property',
                                    'mrp_production_property_rel',
                                    'production_id', 'property_id',
                                    string='Properties')
