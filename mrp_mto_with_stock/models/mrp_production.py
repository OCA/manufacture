# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 John Walsh
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _get_procurement_group_data(self, move):
        return {'partner_id': move.partner_id.id,
                'name': '{0}:{1}'.format(self.name, move.product_id.name)}

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
        procurement_obj = self.env['procurement.group']
        for production in self:
            warehouse = production.location_src_id.get_warehouse()
            mto_with_no_move_dest_id = warehouse.mrp_mto_mts_forecast_qty
            for move in self.move_raw_ids:
                group = new_move = procurement = False
                qty_to_procure = 0.0
                if move.state in ('partially_available', 'confirmed') \
                        and move.location_id in \
                        move.product_id.mrp_mts_mto_location_ids \
                        and not mto_with_no_move_dest_id:
                    # Search procurement group which has created from here
                    group_name = '{0}:{1}'.format(
                        production.name, move.product_id.name)
                    procurement = procurement_obj.search(
                        [('name', '=', group_name)])
                    if not procurement:
                        # We have to split the move because we can't have
                        # a part of the move that have ancestors and not the
                        # other else it won't ever be reserved.
                        qty_to_procure = (
                            move.product_uom_qty - move.reserved_availability)
                        if qty_to_procure < move.product_uom_qty:
                            move._do_unreserve()
                            new_move_id = move._split(
                                qty_to_procure,
                                restrict_partner_id=move.restrict_partner_id)
                            new_move = move_obj.browse(new_move_id)
                            move._action_assign()
                        else:
                            new_move = move
                        pg_data = production._get_procurement_group_data(
                            new_move)
                        group = procurement_obj.create(pg_data)
                if move.state in ('partially_available', 'confirmed') \
                        and move.procure_method == 'make_to_stock' \
                        and mto_with_no_move_dest_id and \
                        move.location_id in \
                        move.product_id.mrp_mts_mto_location_ids:
                    qty_to_procure = production.get_mto_qty_to_procure(move)
                    if qty_to_procure > 0.0:
                        pg_data = production._get_procurement_group_data(move)
                        group = procurement_obj.create(pg_data)
                        new_move = move
                if group:
                    production.run_procurement(new_move, group, qty_to_procure)
        return res

    @api.multi
    def run_procurement(self, move, group, qty):
        self.ensure_one()
        errors = []
        values = move._prepare_procurement_values()
        origin = ((group and group.name + ":") or "") + 'MTO -> Production'
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
