# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 John Walsh
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.exceptions import UserError
import copy


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _mto_with_stock_condition(self, move):
        """Extensibility-enhancer method for modifying the scenarios when
        MTO/MTS method should apply."""
        return move.location_id in move.product_id.mrp_mts_mto_location_ids

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
            move_ids = copy.copy(self.move_raw_ids.ids)
            for move in move_obj.browse(move_ids):
                new_move = False
                qty_to_procure = 0.0
                if move.state in ('partially_available', 'confirmed') \
                        and move.procure_method == 'make_to_stock' \
                        and mto_with_no_move_dest_id and \
                        self._mto_with_stock_condition(move):
                    qty_to_procure = production.get_mto_qty_to_procure(move)
                    if qty_to_procure > 0.0:
                        new_move = move
                    else:
                        continue
                if new_move:
                    production.run_procurement(new_move, qty_to_procure,
                                               mto_with_no_move_dest_id)
        return res

    @api.multi
    def _adjust_procure_method(self):
        """When configured as MTO/MTS manufacturing location, if there is
        stock available unreserved, use it and procure the remaining."""
        res = super()._adjust_procure_method()
        warehouse = self.location_src_id.get_warehouse()
        mto_with_no_move_dest_id = warehouse.mrp_mto_mts_forecast_qty
        for move in self.move_raw_ids:
            if not self._mto_with_stock_condition(move):
                continue
            new_move = False
            qty_to_procure = 0.0
            if not mto_with_no_move_dest_id:
                # We have to split the move because we can't have
                # a part of the move that have ancestors and not the
                # other else it won't ever be reserved.
                qty_to_procure = min(
                    move.product_uom_qty -
                    move.product_id.qty_available_not_res,
                    move.product_uom_qty)
                if 0.0 < qty_to_procure < move.product_uom_qty:
                    # we need to adjust the unit_factor of the stock moves
                    # to split correctly the load of each one.
                    ratio = qty_to_procure / move.product_uom_qty
                    new_move = move.copy({
                        'product_uom_qty': qty_to_procure,
                        'procure_method': 'make_to_order',
                        'unit_factor': move.unit_factor * ratio,
                    })
                    move.write({
                        'product_uom_qty':
                            move.product_uom_qty - qty_to_procure,
                        'unit_factor': move.unit_factor * (1 - ratio),
                    })
                    move._action_confirm()
                    move._action_assign()
                elif qty_to_procure > 0.0:
                    new_move = move
                else:
                    # If we don't need to procure, we reserve the qty
                    # for this move so it won't be available for others,
                    # which would generate planning issues.
                    move._action_confirm()
                    move._action_assign()
            if new_move:
                self.run_procurement(
                    new_move, qty_to_procure, mto_with_no_move_dest_id)
        return res

    @api.multi
    def run_procurement(self, move, qty, mto_with_no_move_dest_id):
        self.ensure_one()
        errors = []
        values = move._prepare_procurement_values()
        # In that mode, we don't want any link between the raw material move
        # And the previous move generated now.
        if mto_with_no_move_dest_id:
            values.pop('move_dest_ids', None)
        origin = self.origin or move.origin
        values['route_ids'] = move.product_id.route_ids
        try:
            self.env['procurement.group'].run(
                move.product_id,
                qty,
                move.product_uom,
                move.location_id,
                origin,
                origin,
                values
            )
        except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True

    @api.model
    def _get_incoming_qty_waiting_validation(self, move):
        """
        This method should be overriden in submodule to manage cases where
        we need to add quantities to the forecast quantity. Like draft
        purchase order, purchase request, etc...
        """
        return 0.0

    @api.multi
    def get_mto_qty_to_procure(self, move):
        self.ensure_one()
        stock_location_id = move.location_id.id
        move_location = move.with_context(location=stock_location_id)
        virtual_available = move_location.product_id.virtual_available
        qty_available = move.product_id.uom_id._compute_quantity(
            virtual_available, move.product_uom)
        draft_incoming_qty = self._get_incoming_qty_waiting_validation(move)
        qty_available += draft_incoming_qty
        if qty_available >= 0:
            return 0.0
        else:
            if abs(qty_available) < move.product_uom_qty:
                return abs(qty_available)
        return move.product_uom_qty
