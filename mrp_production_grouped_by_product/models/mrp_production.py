# Copyright 2018 Tecnativa - David Vidal
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import config


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _post_mo_merging_adjustments(self, vals):
        """Called when a new MO is merged onto existing one for adjusting the
        needed values according this merging.

        :param self: Single record of the target record where merging.
        :param vals: Dictionary with the new record values.
        """
        self.ensure_one()
        new_vals = {
            'origin': (self.origin or '') + ",%s" % vals['origin'],
        }
        if vals.get('move_dest_ids'):
            new_vals['move_dest_ids'] = vals['move_dest_ids']
            self.move_finished_ids.move_dest_ids = vals['move_dest_ids']
        self.write(new_vals)

    def _find_grouping_target(self, vals):
        mo = self.env['mrp.production'].search([
            ('product_id', '=', vals['product_id']),
            ('bom_id', '=', vals.get('bom_id', False)),
            ('routing_id', '=', vals.get('routing_id', False)),
            ('company_id', '=', vals.get('company_id', False)),
            ('state', '=', 'confirmed'),
        ], limit=1)
        return mo

    @api.model
    def create(self, vals):
        context = self.env.context
        if (context.get('group_mo_by_product') and
                (not config['test_enable'] or context.get('test_group_mo'))):
            mo = self._find_grouping_target(vals)
            if mo:
                self.env['change.production.qty'].create({
                    'mo_id': mo.id,
                    'product_qty': mo.product_qty + vals['product_qty'],
                }).change_prod_qty()
                mo._post_mo_merging_adjustments(vals)
                return mo
        return super(MrpProduction, self).create(vals)
