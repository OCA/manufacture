# -*- encoding: utf-8 -*-
from openerp import fields, models, api
import pdb
import logging
_logger = logging.getLogger(__name__)

class mrp_production(models.Model):
    _inherit = 'mrp.production'

#    @api.model
#    def _make_consume_line_from_data(self, production, product, uom_id, qty, uos_id, uos_qty):
#        '''Confirms stock move or put it in waiting if it's linked to another move.
#        @returns list of ids'''
#        pdb.set_trace()
#        # change the qty to make two moves (if needed)
#        res = super(mrp_production, self)._make_consume_line_from_data(production, product, uom_id, uos_id, uos_qty)
#        return res
    @api.one
    def action_confirm(self):
        '''Confirms stock move or put it in waiting if it's linked to another move.
        @returns list of ids'''
#        pdb.set_trace()
        # change the qty to make two moves (if needed)
        res = super(mrp_production, self).action_confirm()
        # try to assign moves (and generate procurements!)
        self.action_assign()
        return res

    @api.one
    def action_assign(self):
        '''Reserves available products to the production order
        but also creates procurements for more items if we 
        cannot reserve enough (MTO with stock)
        @returns list of ids'''
        # reserve all that is available
        res = super(mrp_production, self).action_assign()
        mtos_route = self.env.ref('stock_mts_mto_rule.route_mto_mts')
        for move in self.move_lines:
            if move.state == 'confirmed' and mtos_route.id in move.product_id.route_ids.ids:
                #This move is waiting availability

                #create a domain
                #TODO: check other possible states confirmed/exception?
                domain = [('product_id','=', move.product_id.id),('state','=','running'),('move_dest_id','=',move.id)]
                if move.group_id:
                    domain.append(('group_id','=',move.group_id.id))
                procurement = self.env['procurement.order'].search(domain)
                if not procurement:
                    # we need to create a procurement
                    qty_to_procure = move.remaining_qty - move.reserved_availability
                    proc_dict = self._prepare_mto_procurement(move, qty_to_procure)
                    procurement = self.env['procurement.order'].create(proc_dict)
        return res
    
    def _prepare_mto_procurement(self, move, qty):
        '''Prepares a procurement for a MTO move
        using similar logic to /stock/stock.py/class stock_move/_prepare_procurement_from_move()
        
        '''
        origin = ((move.group_id and (move.group_id.name) + ":") or "") + ((move.name and move.name + ":") or "") + ('MTO -> Production')
        group_id = move.group_id and move.group_id.id or False

        route_ids = [self.env.ref('stock.route_warehouse0_mto')]
        return{
            'name': move.name + ':' + str(move.id),
            'origin': origin,
            'company_id': move.company_id and move.company_id.id or False,
            'date_planned': move.date,
            'product_id': move.product_id.id,
            'product_qty': qty,
            'product_uom': move.product_uom.id,
            'product_uos_qty': qty, #FIXME: (move.product_uos and move.product_uos_qty) or move.product_uom_qty,
            'product_uos': move.product_uom.id, #FIXME:(move.product_uos and move.product_uos.id) or move.product_uom.id,
            'location_id': move.location_id.id,
            'move_dest_id': move.id,
            'group_id': group_id,
            'route_ids':[(4, x.id) for x in route_ids],
            'warehouse_id': move.warehouse_id.id or (move.picking_type_id and move.picking_type_id.warehouse_id.id or False),
            'priority': move.priority,
        }




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

