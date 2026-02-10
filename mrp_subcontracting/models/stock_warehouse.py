# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
# Copyright 2019 Odoo
# Copyright 2020 Tecnativa - Alexandre Díaz
# Copyright 2020 Tecnativa - Pedro M. Baeza

from odoo import api, fields, models, _


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    subcontracting_to_resupply = fields.Boolean(
        'Resupply Subcontractors', default=True,
        help="Resupply subcontractors with components")

    subcontracting_mto_pull_id = fields.Many2one(
        'procurement.rule', 'Subcontracting MTO Rule')
    subcontracting_pull_id = fields.Many2one(
        'procurement.rule', 'Subcontracting MTS Rule')

    subcontracting_route_id = fields.Many2one(
        'stock.location.route', 'Resupply Subcontractor',
        ondelete='restrict')

    subcontracting_type_id = fields.Many2one(
        'stock.picking.type', 'Subcontracting Operation Type',
        domain=[('code', '=', 'mrp_operation')])

    def create_sequences_and_picking_types(self):
        res = super(StockWarehouse, self).create_sequences_and_picking_types()
        self._create_subcontracting_picking_type()
        return res

    @api.multi
    def get_routes_dict(self):
        result = super(StockWarehouse, self).get_routes_dict()
        subcontract_location_id = self._get_subcontracting_location()
        for warehouse in self:
            result[warehouse.id]['subcontract'] = [
                self.Routing(
                    warehouse.lot_stock_id,
                    subcontract_location_id,
                    warehouse.out_type_id),
            ]
        return result

    @api.multi
    def create_routes(self):
        res = super(StockWarehouse, self).create_routes()
        self.ensure_one()
        routes_data = self.get_routes_dict()
        subcontracting_route = self._create_or_update_subcontracting_route(
            routes_data)
        subcontracting_mto_pull = (
            self._create_or_update_subcontracting_mto_pull(routes_data))
        subcontracting_pull = (
            self._create_or_update_subcontracting_pull(routes_data))
        res['subcontracting_route_id'] = subcontracting_route.id
        res['subcontracting_mto_pull_id'] = subcontracting_mto_pull.id
        res['subcontracting_pull_id'] = subcontracting_pull.id
        res.setdefault('route_ids', [])
        res['route_ids'].append((4, subcontracting_route.id))
        return res

    @api.multi
    def write(self, vals):
        if 'subcontracting_to_resupply' in vals:
            if vals.get('subcontracting_to_resupply'):
                for warehouse in self:
                    wh_vals = dict(vals)
                    if not warehouse.subcontracting_mto_pull_id:
                        routes_data = warehouse.get_routes_dict()
                        route = (
                            warehouse
                            ._create_or_update_subcontracting_route(
                                routes_data))
                        mto_pull = (
                            warehouse
                            ._create_or_update_subcontracting_mto_pull(
                                routes_data))
                        pull = (
                            warehouse
                            ._create_or_update_subcontracting_pull(
                                routes_data))
                        wh_vals['subcontracting_route_id'] = route.id
                        wh_vals['subcontracting_mto_pull_id'] = mto_pull.id
                        wh_vals['subcontracting_pull_id'] = pull.id
                        wh_vals['route_ids'] = [(4, route.id)]
                    if not warehouse.subcontracting_type_id:
                        warehouse._create_subcontracting_picking_type()
                    warehouse.subcontracting_type_id.active = False
                    if warehouse.subcontracting_route_id:
                        warehouse.subcontracting_route_id.active = True
                        if warehouse.subcontracting_route_id \
                                not in warehouse.route_ids:
                            wh_vals.setdefault('route_ids', [])
                            wh_vals['route_ids'].append(
                                (4, warehouse.subcontracting_route_id.id))
                    if warehouse.subcontracting_mto_pull_id:
                        warehouse.subcontracting_mto_pull_id.active = True
                    if warehouse.subcontracting_pull_id:
                        warehouse.subcontracting_pull_id.active = True
                    super(StockWarehouse, warehouse).write(wh_vals)
                return True
            else:
                for warehouse in self:
                    if warehouse.subcontracting_type_id:
                        warehouse.subcontracting_type_id.active = False
                    if warehouse.subcontracting_route_id:
                        warehouse.subcontracting_route_id.active = False
                    if warehouse.subcontracting_mto_pull_id:
                        warehouse.subcontracting_mto_pull_id.active = False
                    if warehouse.subcontracting_pull_id:
                        warehouse.subcontracting_pull_id.active = False
        return super(StockWarehouse, self).write(vals)

    @api.multi
    def _get_all_routes(self):
        routes = super(StockWarehouse, self).get_all_routes_for_wh()
        routes |= self.filtered(
            lambda wh: (
                wh.subcontracting_to_resupply
                and wh.subcontracting_route_id
            )
        ).mapped('subcontracting_route_id')
        return routes

    def _create_subcontracting_picking_type(self):
        picking_type_obj = self.env['stock.picking.type']
        seq_obj = self.env['ir.sequence']
        for warehouse in self:
            subcontract_location_id = self._get_subcontracting_location()
            production_location_id = self.env['stock.location'].search(
                [('usage', '=', 'production')], limit=1)
            seq = seq_obj.create({
                'name': warehouse.name + ' ' + _('Sequence Subcontracting'),
                'prefix': warehouse.code + '/SC/',
                'padding': 5,
                'company_id': warehouse.company_id.id,
            })
            other_pick_type = picking_type_obj.search(
                [('warehouse_id', '=', warehouse.id)],
                order='sequence desc', limit=1)
            color = other_pick_type.color if other_pick_type else 0
            max_sequence = (
                other_pick_type and other_pick_type.sequence or 0)
            subcontracting_type = picking_type_obj.create({
                'name': _('Subcontracting'),
                'warehouse_id': warehouse.id,
                'code': 'mrp_operation',
                'use_create_lots': True,
                'use_existing_lots': False,
                'sequence_id': seq.id,
                'default_location_src_id': subcontract_location_id.id,
                'default_location_dest_id': production_location_id.id,
                'sequence': max_sequence + 1,
                'color': color,
                'active': False,
            })
            warehouse.write({
                'subcontracting_type_id': subcontracting_type.id,
            })

    def _get_subcontracting_route_id(self):
        subcontracting_route = self.env.ref(
            'mrp_subcontracting.route_resupply_subcontractor_mto',
            raise_if_not_found=False)
        if not subcontracting_route:
            subcontracting_route = self.env['stock.location.route'].search(
                [('name', 'like', _('Resupply Subcontractor'))], limit=1)
        return subcontracting_route

    def _create_or_update_subcontracting_route(self, routes_data):
        routes_data = routes_data or self.get_routes_dict()
        for warehouse in self:
            if warehouse.subcontracting_route_id:
                subcontracting_route = warehouse.subcontracting_route_id
                subcontracting_route.write({
                    'active': warehouse.subcontracting_to_resupply,
                })
            else:
                subcontracting_route = (
                    self.env['stock.location.route'].create({
                        'name': warehouse._format_routename(
                            name=_('Resupply Subcontractor')),
                        'product_categ_selectable': False,
                        'warehouse_selectable': True,
                        'product_selectable': False,
                        'company_id': warehouse.company_id.id,
                        'sequence': 10,
                        'active': warehouse.subcontracting_to_resupply,
                    }))
            routings = routes_data[warehouse.id]['subcontract']
            dummy, pull_rules_list = (
                warehouse._get_push_pull_rules_values(
                    routings,
                    values={
                        'active': warehouse.subcontracting_to_resupply,
                        'route_id': subcontracting_route.id,
                    }))
            for pull_vals in pull_rules_list:
                existing_pull = self.env['procurement.rule'].search([
                    ('picking_type_id', '=', pull_vals['picking_type_id']),
                    ('location_src_id', '=', pull_vals['location_src_id']),
                    ('location_id', '=', pull_vals['location_id']),
                    ('route_id', '=', pull_vals['route_id']),
                ], limit=1)
                if not existing_pull:
                    self.env['procurement.rule'].create(pull_vals)
                else:
                    existing_pull.write({
                        'active': warehouse.subcontracting_to_resupply,
                    })
        return subcontracting_route

    def _create_or_update_subcontracting_mto_pull(self, routes_data):
        routes_data = routes_data or self.get_routes_dict()
        subcontract_location_id = self._get_subcontracting_location()
        mto_route = self._get_mto_route()
        for warehouse in self:
            mto_vals = {
                'name': warehouse._format_rulename(
                    warehouse.lot_stock_id, subcontract_location_id,
                    _(' MTO')),
                'procure_method': 'make_to_order',
                'company_id': warehouse.company_id.id,
                'action': 'move',
                'auto': 'manual',
                'route_id': mto_route.id,
                'location_id': subcontract_location_id.id,
                'location_src_id': warehouse.lot_stock_id.id,
                'picking_type_id': warehouse.out_type_id.id,
                'active': warehouse.subcontracting_to_resupply,
            }
            if warehouse.subcontracting_mto_pull_id:
                mto_pull = warehouse.subcontracting_mto_pull_id
                mto_pull.write(mto_vals)
            else:
                mto_pull = self.env['procurement.rule'].create(mto_vals)
        return mto_pull

    def _create_or_update_subcontracting_pull(self, routes_data):
        routes_data = routes_data or self.get_routes_dict()
        subcontract_location_id = self._get_subcontracting_location()
        production_location_id = self.env['stock.location'].search(
            [('usage', '=', 'production')], limit=1)
        subcontracting_route = self._get_subcontracting_route_id()
        for warehouse in self:
            pull_vals = {
                'name': warehouse._format_rulename(
                    subcontract_location_id, production_location_id, ''),
                'procure_method': 'make_to_order',
                'company_id': warehouse.company_id.id,
                'action': 'move',
                'auto': 'manual',
                'route_id': subcontracting_route.id,
                'location_id': production_location_id.id,
                'location_src_id': subcontract_location_id.id,
                'picking_type_id': warehouse.out_type_id.id,
                'active': warehouse.subcontracting_to_resupply,
            }
            if warehouse.subcontracting_pull_id:
                pull = warehouse.subcontracting_pull_id
                pull.write(pull_vals)
            else:
                pull = self.env['procurement.rule'].create(pull_vals)
        return pull

    def _get_subcontracting_location(self):
        return self.company_id.subcontracting_location_id

    @api.multi
    def _update_name_and_code(self, name=False, code=False):
        res = super(StockWarehouse, self)._update_name_and_code(name, code)
        for warehouse in self:
            if warehouse.subcontracting_mto_pull_id and name:
                warehouse.subcontracting_mto_pull_id.write({
                    'name': (
                        warehouse.subcontracting_mto_pull_id.name.replace(
                            warehouse.name, name, 1))
                })
            if warehouse.subcontracting_pull_id and name:
                warehouse.subcontracting_pull_id.write({
                    'name': warehouse.subcontracting_pull_id.name.replace(
                        warehouse.name, name, 1)
                })
        return res
