# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
from openerp import _, api, exceptions, fields, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    dismantling = fields.Boolean(string='Dismantling', default=False)
    dismantled_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Dismantled product'
    )
    dismantled_product_tmpl_id = fields.Many2one(
        related='dismantled_product_id.product_tmpl_id',
    )

    _sql_constraints = [
        ('bom_dismantled_product_id',
         'CHECK(dismantled_product_id is not null = dismantling)',
         "Dismantling BoM should have a dismantled product."),
    ]

    @api.multi
    def create_mrp_production(self):
        """ Create a manufacturing order from this BoM
        """
        self.ensure_one()

        product = self._get_bom_product()

        production = self.env['mrp.production'].create({
            'bom_id': self.id,
            'product_id': product.id,
            'product_qty': self.product_qty,
            'product_uom': self.product_uom.id,
        })

        return self._get_form_view('mrp.production', production)

    @api.multi
    def action_create_dismantling_bom(self):
        """ Check dismantling_product_choice config and open choice wizard
        if needed or directly call create_dismantling_bom.
        """
        config_name = 'mrp.bom.dismantling.product_choice'
        if self.env['ir.config_parameter'].get_param(config_name):
            return {
                'type': 'ir.actions.act_window',
                'name': _('Choose main compoment'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mrp.bom.dismantling_product_choice',
                'target': 'new',
                'context': self.env.context
            }

        else:
            return self.create_dismantling_bom()

    @api.multi
    def create_dismantling_bom(self, main_component=None):
        """ Create a dismantling BoM based on this BoM

        If *main_component* is not None, this component will be set as main
        product in dismantling bom.

        Else first component will be taken (sorted by Id).

        :type main_component: product_product
        :rtype: dict
        """
        self.ensure_one()

        self._check_bom_validity(check_dismantling=True)

        product = self._get_bom_product()
        components = self._get_component_needs()

        # If no main component, take first sorted by Id
        if not main_component:
            main_component = sorted(components.keys(), key=lambda c: c.id)[0]

        # Create the BoM on main component
        main_component_needs = components.pop(main_component)
        dismantling_bom = self.create({
            'product_tmpl_id': main_component.product_tmpl_id.id,
            'product_id': main_component.id,
            'dismantling': True,
            'dismantled_product_id': product.id,
            'product_qty': main_component_needs,
        })

        # Create BoM line for self.product_tmpl_id
        self.env['mrp.bom.line'].create({
            'bom_id': dismantling_bom.id,
            'product_id': product.id,
            'product_qty': self.product_qty,
            'product_uom': self.product_uom.id,
        })

        # Add others component as By-products
        subproduct_model = self.env['mrp.subproduct']
        for component, needs in components.items():
            subproduct_model.create({
                'bom_id': dismantling_bom.id,
                'product_id': component.id,
                'product_qty': needs,
                'product_uom': self.env.ref('product.product_uom_unit').id,
            })

        return self._get_form_view('mrp.bom', dismantling_bom)

    def _get_form_view(self, model_name, entity):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': model_name,
            'target': 'current',
            'res_id': entity.id,
            'context': self.env.context
        }

    def _check_bom_validity(self, check_dismantling=False):
        """ Ensure this BoM can be use for creating a dismantling BoM
        or a manufacturing order.

        :type check_dismantling: bool
        :raise exceptions.UserError: If this BoM is not valid.
        """
        warning = None
        if check_dismantling and self.dismantling:
            warning = 'This BoM is already a dismantling Bom.'

        if not len(self.bom_line_ids):
            warning = 'This BoM does not have components.'

        if not self.product_id \
                and len(self.product_tmpl_id.product_variant_ids) > 1:
            warning = 'This product has several variants: ' \
                      'you need to specify one.'

        if warning:
            raise exceptions.UserError(_(warning))

    def _get_component_needs(self):
        """ Return this BoM components and their needed qties.

        The result is like {component_1: 1, component_2: 5, ...}

        :rtype: dict(product_product, float)
        """
        components = self.product_id._get_component_needs(
            product=self.product_id, bom=self
        )
        return dict(components)

    def _get_bom_product(self):
        """ Get the product of this BoM.

        If BoM does not have product_id, return first template variant.

        :rtype: product_product
        """
        if not self.product_id:
            product = self.product_tmpl_id.product_variant_ids[0]
        else:
            product = self.product_id
        return product

    def _bom_find(self, cr, uid, product_tmpl_id=None,
                  product_id=None, properties=None, context=None):
        """Override of the mrp.bom function to avoid mixing
        a BOM and dismantling BOM when they have a product in common
        That can lead to endless recursive loops in computed BOM
        structure
        """
        if not context:
            context = {}
        if properties is None:
            properties = []
        if product_id:
            if not product_tmpl_id:
                product_tmpl_id = self.pool['product.product'].browse(
                    cr, uid, product_id, context=context).product_tmpl_id.id
            domain = [
                '|',
                ('product_id', '=', product_id),
                '&',
                ('product_id', '=', False),
                ('product_tmpl_id', '=', product_tmpl_id)
            ]
        elif product_tmpl_id:
            domain = [('product_id', '=', False),
                      ('product_tmpl_id', '=', product_tmpl_id)]
        else:
            # neither product nor template, makes no sense to search
            return False
        if context.get('company_id'):
            domain = domain + [('company_id', '=', context['company_id'])]
        domain = domain + [
            '|', ('date_start', '=', False),
            ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
            '|', ('date_stop', '=', False),
            ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
        ]
        # Customisation to avoid mixing bom and dismantling
        is_dismantling = context.get('is_dismantling', False)
        domain += [('dismantling', '=', is_dismantling)]

        # order to prioritize bom with product_id over the one without
        ids = self.search(cr, uid, domain,
                          order='sequence, product_id', context=context)
        # Search a BoM which has all properties specified,
        # or if you can not find one, you could
        # pass a BoM without any properties with the smallest sequence
        bom_empty_prop = False
        for bom in self.pool.get('mrp.bom').browse(cr, uid, ids,
                                                   context=context):
            pr = set(map(int, bom.property_ids or [])) - set(properties or [])
            if not pr:
                if not properties or bom.property_ids:
                    return bom.id
                elif not bom_empty_prop:
                    bom_empty_prop = bom.id
        return bom_empty_prop
