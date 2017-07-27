# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 John Walsh
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
import logging
_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def _adjust_procure_method(self):
        # Si location => By pass method...
        super(MrpProduction, self)._adjust_procure_method()

    @api.multi
    def action_assign(self):
        """Reserves available products to the production order but also creates
        procurements for more items if we cannot reserve enough (MTO with
        stock).
        @returns True"""
        # reserve all that is available (standard behaviour):
        res = super(MrpProduction, self).action_assign()
        # try to create procurements:
        move_obj = self.env['stock.move']
        for production in self:
            warehouse = production.location_src_id.get_warehouse()
            mto_with_no_move_dest_id = warehouse.mrp_mto_mts_forecast_qty
            for move in self.move_raw_ids:
                if (move.state == 'confirmed' and move.location_id in
                        move.product_id.mrp_mts_mto_location_ids and not
                        mto_with_no_move_dest_id):
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
                            new_move_id = move.split(
                                qty_to_procure,
                                restrict_lot_id=move.restrict_lot_id,
                                restrict_partner_id=move.restrict_partner_id)
                            new_move = move_obj.browse(
                                new_move_id)
                            move.action_assign()
                        else:
                            new_move = move

                        proc_dict = self._prepare_mto_procurement(
                            new_move, qty_to_procure,
                            mto_with_no_move_dest_id)
                        self.env['procurement.order'].create(proc_dict)

                if (move.state == 'confirmed' and move.location_id in
                        move.product_id.mrp_mts_mto_location_ids and
                        move.procure_method == 'make_to_stock' and
                        mto_with_no_move_dest_id):
                    qty_to_procure = production.get_mto_qty_to_procure(move)
                    if qty_to_procure > 0.0:
                        proc_dict = self._prepare_mto_procurement(
                            move, qty_to_procure, mto_with_no_move_dest_id)
                        proc_dict.pop('move_dest_id', None)
                        self.env['procurement.order'].create(proc_dict)
        return res

    def _prepare_mto_procurement(self, move, qty, mto_with_no_move_dest_id):
        """Prepares a procurement for a MTO product."""
        origin = ((move.group_id and move.group_id.name + ":") or "") + \
                 ((move.name and move.name + ":") or "") + 'MTO -> Production'
        group_id = move.group_id and move.group_id.id or False
        route_ids = self.env.ref('stock.route_warehouse0_mto')
        warehouse_id = (move.warehouse_id.id or (move.picking_type_id and
                        move.picking_type_id.warehouse_id.id or False))
        vals = {
            'name': move.name + ':' + str(move.id),
            'origin': origin,
            'company_id': move.company_id and move.company_id.id or False,
            'date_planned': move.date,
            'product_id': move.product_id.id,
            'product_qty': qty,
            'product_uom': move.product_uom.id,
            'location_id': move.location_id.id,
            'group_id': group_id,
            'route_ids': [(6, 0, route_ids.ids)],
            'warehouse_id': warehouse_id,
            'priority': move.priority,
        }
        if not mto_with_no_move_dest_id:
            vals['move_dest_id'] = move.id
        return vals

    @api.multi
    def get_mto_qty_to_procure(self, move):
        self.ensure_one()
        stock_location_id = move.location_id.id
        move_location = move.with_context(location=stock_location_id)
        virtual_available = move_location.product_id.virtual_available
        qty_available = move.product_id.uom_id._compute_quantity(
            virtual_available, move.product_uom)
        if qty_available >= 0:
            return 0.0
        else:
            if abs(qty_available) < move.product_uom_qty:
                return abs(qty_available)
        return move.product_uom_qty
