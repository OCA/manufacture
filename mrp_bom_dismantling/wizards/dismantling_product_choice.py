# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import _, api, fields, models
from openerp.exceptions import UserError


class DismantlingProductChoice(models.TransientModel):
    _name = 'mrp.bom.dismantling_product_choice'

    def _get_bom_id(self):
        return self.env['mrp.bom'].browse(self.env.context['active_id'])

    bom_id = fields.Many2one(
        'mrp.bom',
        default=_get_bom_id
    )
    component_id = fields.Many2one(
        'product.product',
        required=True,
        domain=[('id', '=', False)]
    )

    @api.onchange('bom_id')
    def on_change_bom_id(self):
        """ Update component_id domain to include only BOM components.
        """
        component_ids = sorted(
            [c.id for c in self.bom_id._get_component_needs()]
        )
        if not component_ids:
            raise UserError(_('This BoM does not have components.'))

        return {
            'domain': {
                'component_id': [('id', 'in', component_ids)]
            }
        }

    @api.multi
    def create_bom(self):
        """ Call dismantling bom creation method with main component specified.
        """
        return self.bom_id.create_dismantling_bom(
            main_component=self.component_id
        )
