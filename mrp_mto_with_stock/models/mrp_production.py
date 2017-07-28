# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 John Walsh
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, _
from openerp.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def action_mass_assign(self):
        if any([x != 'confirmed' for x in self.mapped('state')]):
            raise UserError(_(
                "All Manufacturing Orders must be confirmed."))
        return self.action_assign()

    @api.multi
    def action_assign(self):
        """Reserves available products to the production order but also creates
        procurements for more items if we cannot reserve enough (MTO with
        stock).
        @returns list of ids"""
        # reserve all that is available (standard behaviour):
        res = super(MrpProduction, self).action_assign()
        # try to create procurements:
        move_obj = self.env['stock.move']
        for production in self:
            for move in production.move_lines:
                if (move.state == 'confirmed' and move.location_id in
                        move.product_id.mrp_mts_mto_location_ids):
                    domain = [('product_id', '=', move.product_id.id),
                              ('move_dest_id', '=', move.id)]
                    if move.group_id:
                        domain.append(('group_id', '=', move.group_id.id))
                    procurement = self.env['procurement.order'].search(domain)
                    if not procurement:
                        # We have to split the move because we can't have
                        # a part of the move that have ancestors and not the
                        # other else it won't ever be reserved.
                        qty_to_procure = (move.remaining_qty -
                                          move.reserved_availability)
                        if qty_to_procure < move.product_uom_qty:
                            move.do_unreserve()
                            new_move_id = move_obj.split(
                                move,
                                qty_to_procure,
                                restrict_lot_id=move.restrict_lot_id,
                                restrict_partner_id=move.restrict_partner_id)
                            new_move = move_obj.browse(
                                new_move_id)
                            move.action_assign()
                        else:
                            new_move = move

                        proc_dict = self._prepare_mto_procurement(
                            new_move, qty_to_procure)
                        self.env['procurement.order'].create(proc_dict)
        return res

    def _prepare_mto_procurement(self, move, qty):
        """Prepares a procurement for a MTO product."""
        origin = ((move.group_id and move.group_id.name + ":") or "") + \
                 ((move.name and move.name + ":") or "") + 'MTO -> Production'
        group_id = move.group_id and move.group_id.id or False
        route_ids = self.env.ref('stock.route_warehouse0_mto')
        warehouse_id = (move.warehouse_id.id or (move.picking_type_id and
                        move.picking_type_id.warehouse_id.id or False))
        return {
            'name': move.name + ':' + str(move.id),
            'origin': origin,
            'company_id': move.company_id and move.company_id.id or False,
            'date_planned': move.date,
            'product_id': move.product_id.id,
            'product_qty': qty,
            'product_uom': move.product_uom.id,
            'location_id': move.location_id.id,
            'move_dest_id': move.id,
            'group_id': group_id,
            'route_ids': [(6, 0, route_ids.ids)],
            'warehouse_id': warehouse_id,
            'priority': move.priority,
        }
