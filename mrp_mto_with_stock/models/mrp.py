# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 John Walsh
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models
import logging
_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.one
    def action_confirm(self):
        """Confirms stock move or put it in waiting if it's linked to another move.
        @returns list of ids"""
        # change the qty to make two moves (if needed)
        res = super(MrpProduction, self).action_confirm()
        # try to assign moves (and generate procurements!)
        self.action_assign()
        return res

    @api.one
    def action_assign(self):
        """Reserves available products to the production order but also reates
        procurements for more items if we cannot reserve enough (MTO with
        stock).
        @returns list of ids"""
        # reserve all that is available (standard behaviour):
        res = super(MrpProduction, self).action_assign()
        # try to create procurements:
        mtos_route = self.env.ref('stock_mts_mto_rule.route_mto_mts')
        for move in self.move_lines:
            if (move.state == 'confirmed' and mtos_route.id in
                    move.product_id.route_ids.ids):
                domain = [('product_id', '=', move.product_id.id),
                          ('state', '=', 'running'),
                          ('move_dest_id', '=', move.id)]
                if move.group_id:
                    domain.append(('group_id', '=', move.group_id.id))
                procurement = self.env['procurement.order'].search(domain)
                if not procurement:
                    qty_to_procure = (move.remaining_qty -
                                      move.reserved_availability)
                    proc_dict = self._prepare_mto_procurement(
                        move, qty_to_procure)
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
