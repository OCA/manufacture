# Copyright 2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def _get_incoming_qty_waiting_validation(self, move):
        qty = super(MrpProduction, self)._get_incoming_qty_waiting_validation(
            move)
        location_ids = self.env['stock.location'].search(
            [('id', 'child_of', move.location_id.id)])
        picking_types = self.env['stock.picking.type'].search(
            [('default_location_dest_id', 'in',
              location_ids.ids)])
        orders = self.env['purchase.order'].search(
            [('picking_type_id', 'in', picking_types.ids),
             ('state', 'in', ['draft', 'sent', 'to approve'])])
        po_lines = self.env['purchase.order.line'].search(
            [('order_id', 'in', orders.ids),
             ('product_qty', '>', 0.0),
             ('product_id', '=', move.product_id.id)])
        for line in po_lines:
            qty_uom = line.product_uom._compute_quantity(
                line.product_qty, move.product_uom)
            qty += qty_uom
        return qty
