# -*- coding: utf-8 -*-
# Copyright 2018 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    root_id = fields.Many2one(
        'mrp.production', u"Root order",
        index=True, ondelete='restrict', readonly=True)
    parent_id = fields.Many2one(
        'mrp.production', u"Parent order",
        index=True, ondelete='restrict', readonly=True)
    child_ids = fields.One2many(
        'mrp.production', 'parent_id', u"Child orders",
        domain=[('state', '!=', 'cancel')])

    @api.multi
    def _generate_moves(self):
        """Overloaded to pass the created production order ID in the context.
        It will be used by the 'procurement_order.make_mo()' overload to
        set the parent relation between production orders.
        """
        for prod in self:
            # Set the initial root production order ID
            if not prod.env.context.get('root_mrp_production_id'):
                prod = prod.with_context(root_mrp_production_id=self.id)
            # Set the parent production order ID
            prod = prod.with_context(parent_mrp_production_id=self.id)
            super(MrpProduction, prod)._generate_moves()
        return True

    @api.multi
    def open_production_tree(self):
        self.ensure_one()
        if self.child_ids:
            return {
                'domain': "[('id', '=', %s)]" % self.id,
                'name': _(u"Hierarchy"),
                'view_type': 'tree',
                'view_mode': 'tree',
                'res_model': 'mrp.production',
                'view_id': self.env.ref(
                    'mrp_production_hierarchy.'
                    'mrp_production_tree_view_field_parent').id,
                'target': 'current',
                'type': 'ir.actions.act_window',
                'context': dict(self.env.context),
            }
        return False
