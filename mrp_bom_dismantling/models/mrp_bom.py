# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, api, exceptions, fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    dismantling = fields.Boolean(string='Dismantling', default=False)
    dismantled_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Dismantled product'
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
