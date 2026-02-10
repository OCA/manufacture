# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
# Copyright 2019 Odoo
# Copyright 2020 Tecnativa - Alexandre Díaz
# Copyright 2020 Tecnativa - Pedro M. Baeza

from odoo.tests.common import TransactionCase
from .common import TestMrpSubcontractingCommon


class TestSubcontractingBasic(TransactionCase):
    def test_subcontracting_location_1(self):
        self.assertTrue(self.env.user.company_id.subcontracting_location_id)
        self.assertTrue(
            self.env.user.company_id.subcontracting_location_id.active)
        company2 = self.env['res.company'].create({'name': 'Test Company'})
        self.assertTrue(company2.subcontracting_location_id)
        self.assertTrue(
            self.env.user.company_id.subcontracting_location_id
            != company2.subcontracting_location_id)


class TestSubcontractingFlows(TestMrpSubcontractingCommon):
    def test_flow_1(self):
        picking_receipt = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'partner_id': self.subcontractor_partner1.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'move_lines': [(0, 0, {
                'name': self.finished.name,
                'product_id': self.finished.id,
                'product_uom_qty': 1,
                'product_uom': self.finished.uom_id.id,
                'location_id': self.env.ref('stock.stock_location_suppliers').id,
                'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            })],
        })
        picking_receipt.action_confirm()
        self.assertTrue(all(
            m.product_uom_qty == m.reserved_availability
            for m in picking_receipt.move_lines))
        self.assertEqual(picking_receipt.state, 'assigned')
        self.assertFalse(picking_receipt.display_action_record_components)
        mo = self.env['mrp.production'].search([('bom_id', '=', self.bom.id)])
        self.assertEqual(len(mo), 1)
        wh = picking_receipt.picking_type_id.warehouse_id
        self.assertEquals(mo.picking_type_id, wh.subcontracting_type_id)
        self.assertFalse(mo.picking_type_id.active)
        pg1 = self.env['procurement.group'].create({})
        self.env['stock.warehouse.orderpoint'].create({
            'name': 'xxx',
            'product_id': self.comp1.id,
            'product_min_qty': 0,
            'product_max_qty': 0,
            'location_id':
                self.env.user.company_id.subcontracting_location_id.id,
            'group_id': pg1.id,
        })
        self.env['procurement.group'].run_scheduler()
        picking = self.env['stock.picking'].search([('group_id', '=', pg1.id)])
        self.assertEqual(len(picking), 1)
        self.assertEquals(picking.picking_type_id, wh.out_type_id)
        picking_receipt.move_lines.quantity_done = 1
        picking_receipt.button_validate()
        self.assertEquals(mo.state, 'done')
        avail_qty_comp1 = self.env['stock.quant']._get_available_quantity(
            self.comp1,
            self.subcontractor_partner1.property_stock_subcontractor,
            allow_negative=True)
        avail_qty_comp2 = self.env['stock.quant']._get_available_quantity(
            self.comp2,
            self.subcontractor_partner1.property_stock_subcontractor,
            allow_negative=True)
        avail_qty_finished = self.env['stock.quant']._get_available_quantity(
            self.finished, wh.lot_stock_id)
        self.assertEquals(avail_qty_comp1, -1)
        self.assertEquals(avail_qty_comp2, -1)
        self.assertEquals(avail_qty_finished, 1)
        return_wizard = self.env['stock.return.picking'].with_context(
            active_id=picking_receipt.id, active_model='stock.picking',
        ).create({})
        return_picking_id, pick_type_id = return_wizard._create_returns()
        return_picking = self.env['stock.picking'].browse(return_picking_id)
        self.assertEqual(len(return_picking), 1)
        self.assertEqual(
            return_picking.move_lines.location_dest_id,
            self.subcontractor_partner1.property_stock_subcontractor)

    def test_flow_2(self):
        resupply_sub_on_order_route = self.env['stock.location.route'].search([
            ('name', '=', 'Resupply Subcontractor on Order')])
        (self.comp1 + self.comp2).write({
            'route_ids': [(4, resupply_sub_on_order_route.id)]})
        partner_subcontract_location = self.env['stock.location'].create({
            'name': 'Specific partner location',
            'location_id': self.env.ref(
                'stock.stock_location_locations_partner').id,
            'usage': 'internal',
            'company_id': self.env.user.company_id.id,
        })
        self.subcontractor_partner1.property_stock_subcontractor = (
            partner_subcontract_location.id)
        resupply_rule = resupply_sub_on_order_route.pull_ids.filtered(
            lambda l: (
                l.location_id == self.comp1.property_stock_production and
                l.location_src_id ==
                self.env.user.company_id.subcontracting_location_id))
        resupply_rule.copy({
            'location_src_id': partner_subcontract_location.id})
        resupply_warehouse_rule = (
            self.warehouse.mapped('route_ids.pull_ids').filtered(
                lambda l: (
                    l.location_id ==
                    self.env.user.company_id.subcontracting_location_id and
                    l.location_src_id == self.warehouse.lot_stock_id)))
        for warehouse_rule in resupply_warehouse_rule:
            warehouse_rule.copy({
                'location_id': partner_subcontract_location.id})
        picking_receipt = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'partner_id': self.subcontractor_partner1.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'move_lines': [(0, 0, {
                'name': self.finished.name,
                'product_id': self.finished.id,
                'product_uom_qty': 1,
                'product_uom': self.finished.uom_id.id,
                'location_id': self.env.ref('stock.stock_location_suppliers').id,
                'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            })],
        })
        picking_receipt.action_confirm()
        self.assertFalse(picking_receipt.display_action_record_components)
        mo = self.env['mrp.production'].search([('bom_id', '=', self.bom.id)])
        self.assertEquals(mo.state, 'confirmed')
        picking = mo.move_raw_ids.mapped('move_orig_ids.picking_id')
        self.assertEqual(len(picking), 1)
        self.assertEqual(len(picking.move_lines), 2)
        wh = picking.picking_type_id.warehouse_id
        self.assertEquals(picking.picking_type_id, wh.out_type_id)
        self.assertEquals(mo.picking_type_id, wh.subcontracting_type_id)
        self.assertFalse(mo.picking_type_id.active)
        comp2mo = self.env['mrp.production'].search([
            ('bom_id', '=', self.comp2_bom.id)])
        self.assertEqual(len(comp2mo), 0)
        picking_receipt.move_lines.quantity_done = 1
        picking_receipt.button_validate()
        self.assertEquals(mo.state, 'done')
        avail_qty_comp1 = self.env['stock.quant']._get_available_quantity(
            self.comp1,
            self.subcontractor_partner1.property_stock_subcontractor,
            allow_negative=True)
        avail_qty_comp2 = self.env['stock.quant']._get_available_quantity(
            self.comp2,
            self.subcontractor_partner1.property_stock_subcontractor,
            allow_negative=True)
        avail_qty_finished = self.env['stock.quant']._get_available_quantity(
            self.finished, wh.lot_stock_id)
        self.assertEquals(avail_qty_comp1, -1)
        self.assertEquals(avail_qty_comp2, -1)
        self.assertEquals(avail_qty_finished, 1)
        avail_qty_comp1_in_global_location = (
            self.env['stock.quant']._get_available_quantity(
                self.comp1,
                self.env.user.company_id.subcontracting_location_id,
                allow_negative=True))
        avail_qty_comp2_in_global_location = (
            self.env['stock.quant']._get_available_quantity(
                self.comp2,
                self.env.user.company_id.subcontracting_location_id,
                allow_negative=True))
        self.assertEqual(avail_qty_comp1_in_global_location, 0.0)
        self.assertEqual(avail_qty_comp2_in_global_location, 0.0)

    def test_flow_3(self):
        resupply_sub_on_order_route = self.env.ref(
            'mrp_subcontracting.route_resupply_subcontractor_mto')
        (self.comp1 + self.comp2).write({
            'route_ids': [(4, resupply_sub_on_order_route.id, None)]})
        mto_route = self.env.ref('stock.route_warehouse0_mto')
        manufacture_route = self.env.ref('mrp.route_warehouse0_manufacture')
        self.comp2.write({'route_ids': [
            (5, False),
            (4, manufacture_route.id, None),
            (4, mto_route.id, None),
        ]})
        picking_receipt = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'partner_id': self.subcontractor_partner1.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'move_lines': [(0, 0, {
                'name': self.finished.name,
                'product_id': self.finished.id,
                'product_uom_qty': 1,
                'product_uom': self.finished.uom_id.id,
                'location_id': self.env.ref('stock.stock_location_suppliers').id,
                'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            })],
        })
        picking_receipt.action_confirm()
        self.assertFalse(picking_receipt.display_action_record_components)
        mo = self.env['mrp.production'].search([('bom_id', '=', self.bom.id)])
        self.assertEquals(mo.state, 'confirmed')
        picking_delivery = mo.move_raw_ids.mapped('move_orig_ids.picking_id')
        self.assertEqual(len(picking_delivery), 1)
        self.assertEqual(len(picking_delivery.move_lines), 2)
        self.assertEquals(picking_delivery.origin, picking_receipt.name)
        self.assertEquals(
            picking_delivery.partner_id, picking_receipt.partner_id)
        wh = picking_receipt.picking_type_id.warehouse_id
        self.assertEquals(picking_delivery.picking_type_id, wh.out_type_id)
        self.assertEquals(mo.picking_type_id, wh.subcontracting_type_id)
        self.assertFalse(mo.picking_type_id.active)
        comp2mo = self.env['mrp.production'].search([
            ('bom_id', '=', self.comp2_bom.id)])
        self.assertEqual(len(comp2mo), 1)
        picking_receipt.move_lines.quantity_done = 1
        picking_receipt.button_validate()
        self.assertEquals(mo.state, 'done')
        avail_qty_comp1 = self.env['stock.quant']._get_available_quantity(
            self.comp1,
            self.subcontractor_partner1.property_stock_subcontractor,
            allow_negative=True)
        avail_qty_comp2 = self.env['stock.quant']._get_available_quantity(
            self.comp2,
            self.subcontractor_partner1.property_stock_subcontractor,
            allow_negative=True)
        avail_qty_finished = self.env['stock.quant']._get_available_quantity(
            self.finished, wh.lot_stock_id)
        self.assertEquals(avail_qty_comp1, -1)
        self.assertEquals(avail_qty_comp2, -1)
        self.assertEquals(avail_qty_finished, 1)

    def test_flow_4(self):
        mto_route = self.env.ref('stock.route_warehouse0_mto')
        manufacture_route = self.env.ref('mrp.route_warehouse0_manufacture')
        self.comp2.write({'route_ids': [
            (5, False),
            (4, manufacture_route.id, None),
            (4, mto_route.id, None),
        ]})
        self.env['stock.warehouse.orderpoint'].create({
            'product_id': self.comp2.id,
            'product_min_qty': 0.0,
            'product_max_qty': 10.0,
            'location_id': self.env.user.company_id.subcontracting_location_id.id,
        })
        picking_receipt = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'partner_id': self.subcontractor_partner1.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'move_lines': [(0, 0, {
                'name': self.finished.name,
                'product_id': self.finished.id,
                'product_uom_qty': 1,
                'product_uom': self.finished.uom_id.id,
                'location_id': self.env.ref('stock.stock_location_suppliers').id,
                'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            })],
        })
        picking_receipt.action_confirm()
        warehouse = picking_receipt.picking_type_id.warehouse_id
        mo = self.env['mrp.production'].search([('bom_id', '=', self.bom.id)])
        self.assertEquals(mo.state, 'confirmed')
        move = self.env['stock.move'].search([
            ('product_id', '=', self.comp2.id),
            ('location_id', '=', warehouse.lot_stock_id.id),
            ('location_dest_id', '=',
             self.env.user.company_id.subcontracting_location_id.id),
        ])
        self.assertTrue(move)
        picking_delivery = move.picking_id
        self.assertTrue(picking_delivery)
        self.assertEqual(move.product_uom_qty, 1.0)
        comp2mo = self.env['mrp.production'].search([
            ('bom_id', '=', self.comp2_bom.id)])
        self.assertEqual(len(comp2mo), 1)

    def test_flow_5(self):
        main_partner_2 = self.env['res.partner'].create({
            'name': 'main_partner'})
        subcontractor_partner2 = self.env['res.partner'].create({
            'name': 'subcontractor_partner',
            'parent_id': main_partner_2.id,
            'company_id': self.env.ref('base.main_company').id
        })
        comp3 = self.env['product.product'].create({
            'name': 'Component1',
            'type': 'product',
            'categ_id': self.env.ref('product.product_category_all').id,
        })
        bom2 = self.env['mrp.bom'].create({
            'type': 'subcontract',
            'product_tmpl_id': self.finished.product_tmpl_id.id,
            'bom_line_ids': [
                (0, 0, {
                    'product_id': self.comp1.id,
                    'product_qty': 1,
                }),
                (0, 0, {
                    'product_id': comp3.id,
                    'product_qty': 1,
                }),
            ],
        })
        self.bom.write({'subcontractor_ids': [
            (4, self.subcontractor_partner1.id, None)]})
        bom2.write({'subcontractor_ids': [
            (4, subcontractor_partner2.id, None)]})
        picking_receipt1 = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'partner_id': self.subcontractor_partner1.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'move_lines': [(0, 0, {
                'name': self.finished.name,
                'product_id': self.finished.id,
                'product_uom_qty': 1,
                'product_uom': self.finished.uom_id.id,
                'location_id': self.env.ref('stock.stock_location_suppliers').id,
                'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            })],
        })
        picking_receipt1.action_confirm()
        picking_receipt2 = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'partner_id': subcontractor_partner2.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'move_lines': [(0, 0, {
                'name': self.finished.name,
                'product_id': self.finished.id,
                'product_uom_qty': 1,
                'product_uom': self.finished.uom_id.id,
                'location_id': self.env.ref('stock.stock_location_suppliers').id,
                'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            })],
        })
        picking_receipt2.action_confirm()
        mo_pick1 = picking_receipt1.move_lines.mapped(
            'move_orig_ids.production_id')
        mo_pick2 = picking_receipt2.move_lines.mapped(
            'move_orig_ids.production_id')
        self.assertEquals(len(mo_pick1), 1)
        self.assertEquals(len(mo_pick2), 1)
        self.assertEquals(mo_pick1.bom_id, self.bom)
        self.assertEquals(mo_pick2.bom_id, bom2)

    def test_flow_6(self):
        main_partner_2 = self.env['res.partner'].create({
            'name': 'main_partner'})
        subcontractor_partner2 = self.env['res.partner'].create({
            'name': 'subcontractor_partner',
            'parent_id': main_partner_2.id,
            'company_id': self.env.ref('base.main_company').id,
        })
        self.env.cache.invalidate()

        comp3 = self.env['product.product'].create({
            'name': 'Component3',
            'type': 'product',
            'categ_id': self.env.ref('product.product_category_all').id,
        })

        bom2 = self.env['mrp.bom'].create({
            'type': 'subcontract',
            'product_tmpl_id': self.finished.product_tmpl_id.id,
            'bom_line_ids': [
                (0, 0, {
                    'product_id': self.comp1.id,
                    'product_qty': 1,
                }),
                (0, 0, {
                    'product_id': comp3.id,
                    'product_qty': 2,
                }),
            ],
        })

        self.bom.write({'subcontractor_ids': [
            (4, self.subcontractor_partner1.id, None)]})
        bom2.write({'subcontractor_ids': [
            (4, subcontractor_partner2.id, None)]})

        picking_receipt = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'partner_id': subcontractor_partner2.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'move_lines': [(0, 0, {
                'name': self.finished.name,
                'product_id': self.finished.id,
                'product_uom_qty': 1,
                'product_uom': self.finished.uom_id.id,
                'location_id': self.env.ref('stock.stock_location_suppliers').id,
                'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            })],
        })
        picking_receipt.action_confirm()

        picking_receipt.move_lines.quantity_done = 3.0
        picking_receipt.action_done()
        mo = picking_receipt._get_subcontracted_productions()
        move_comp1 = mo.move_raw_ids.filtered(
            lambda m: m.product_id == self.comp1)
        move_comp3 = mo.move_raw_ids.filtered(lambda m: m.product_id == comp3)
        self.assertEqual(sum(move_comp1.mapped('product_uom_qty')), 3.0)
        self.assertEqual(sum(move_comp3.mapped('product_uom_qty')), 6.0)
        self.assertEqual(sum(move_comp1.mapped('quantity_done')), 3.0)
        self.assertEqual(sum(move_comp3.mapped('quantity_done')), 6.0)
        move_finished = mo.move_finished_ids
        self.assertEqual(sum(move_finished.mapped('product_uom_qty')), 3.0)
        self.assertEqual(sum(move_finished.mapped('quantity_done')), 3.0)

    def test_flow_7(self):
        (self.comp1 | self.comp2 | self.finished).write({'tracking': 'lot'})
        picking_receipt = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'partner_id': self.subcontractor_partner1.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'move_lines': [(0, 0, {
                'name': self.finished.name,
                'product_id': self.finished.id,
                'product_uom_qty': 5,
                'product_uom': self.finished.uom_id.id,
                'location_id': self.env.ref('stock.stock_location_suppliers').id,
                'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            })],
        })
        picking_receipt.action_confirm()
        mo = picking_receipt.move_lines.move_orig_ids.production_id
        move_comp1 = mo.move_raw_ids.filtered(
            lambda m: m.product_id == self.comp1)
        move_comp2 = mo.move_raw_ids.filtered(
            lambda m: m.product_id == self.comp2)
        move_finished = picking_receipt.move_lines
        self.assertEqual(move_comp1.quantity_done, 0)
        self.assertEqual(move_comp2.quantity_done, 0)
        lot_c1 = self.env['stock.production.lot'].create({
            'name': 'LOT C1',
            'product_id': self.comp1.id,
        })
        lot_c2 = self.env['stock.production.lot'].create({
            'name': 'LOT C2',
            'product_id': self.comp2.id,
        })
        lot_f1 = self.env['stock.production.lot'].create({
            'name': 'LOT F1',
            'product_id': self.finished.id,
        })
        context = {
            'active_id': picking_receipt._get_subcontracted_productions().id,
            'default_subcontract_move_id': picking_receipt.move_lines.id,
        }
        register_wizard = self.env['mrp.product.produce'].with_context(
            context).create({
            'product_qty': 3.0,
            'lot_id': lot_f1.id,
        })
        produce_lines = move_comp1 + move_comp2
        register_wizard.write({
            'produce_line_ids': [
                (0, 0, {
                    'move_id': move_comp1.id,
                    'product_id': self.comp1.id,
                    'qty_done': 3.0,
                    'lot_id': lot_c1.id,
                }),
                (0, 0, {
                    'move_id': move_comp2.id,
                    'product_id': self.comp2.id,
                    'qty_done': 3.0,
                    'lot_id': lot_c2.id,
                }),
            ],
        })
        register_wizard.do_produce()
        register_wizard2 = self.env['mrp.product.produce'].with_context(
            context).create({
            'product_qty': 2.0,
            'lot_id': lot_f1.id,
        })
        register_wizard2.write({
            'produce_line_ids': [
                (0, 0, {
                    'move_id': move_comp1.id,
                    'product_id': self.comp1.id,
                    'qty_done': 2.0,
                    'lot_id': lot_c1.id,
                }),
                (0, 0, {
                    'move_id': move_comp2.id,
                    'product_id': self.comp2.id,
                    'qty_done': 2.0,
                    'lot_id': lot_c2.id,
                }),
            ],
        })
        register_wizard2.do_produce()
        self.assertEqual(move_comp1.quantity_done, 5.0)
        self.assertEqual(
            move_comp1.move_line_ids.mapped('lot_id.name')[0], 'LOT C1')
        self.assertEqual(move_comp2.quantity_done, 5.0)
        self.assertEqual(
            move_comp2.move_line_ids.mapped('lot_id.name')[0], 'LOT C2')
        self.assertEqual(move_finished.quantity_done, 5.0)
        self.assertEqual(
            move_finished.move_line_ids.mapped('lot_id.name')[0], 'LOT F1')
        corrected_final_lot = self.env['stock.production.lot'].create({
            'name': 'LOT F2',
            'product_id': self.finished.id,
        })
        for ml in picking_receipt.move_lines.move_line_ids:
            if ml.qty_done:
                ml.write({'lot_id': corrected_final_lot.id})
        orig_moves = picking_receipt.move_lines.move_orig_ids
        move_raw_comp_1 = orig_moves.production_id.move_raw_ids.filtered(
            lambda m: m.product_id == self.comp1)
        move_raw_comp_2 = orig_moves.production_id.move_raw_ids.filtered(
            lambda m: m.product_id == self.comp2)
        for ml in move_raw_comp_1.move_line_ids:
            if ml.qty_done:
                ml.write({'lot_produced_id': corrected_final_lot.id})
        for ml in move_raw_comp_2.move_line_ids:
            if ml.qty_done:
                ml.write({'lot_produced_id': corrected_final_lot.id})
        self.assertEqual(
            move_comp1.move_line_ids.mapped('lot_produced_id.name')[0],
            'LOT F2')
        self.assertEqual(
            move_comp2.move_line_ids.mapped('lot_produced_id.name')[0],
            'LOT F2')

    def test_flow_8(self):
        resupply_sub_on_order_route = self.env['stock.location.route'].search([
            ('name', '=', 'Resupply Subcontractor on Order')])
        (self.comp1 + self.comp2).write({
            'route_ids': [(4, resupply_sub_on_order_route.id, None)]})
        picking_receipt = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'partner_id': self.subcontractor_partner1.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'move_lines': [(0, 0, {
                'name': self.finished.name,
                'product_id': self.finished.id,
                'product_uom_qty': 5,
                'product_uom': self.finished.uom_id.id,
                'location_id': self.env.ref('stock.stock_location_suppliers').id,
                'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            })],
        })
        picking_receipt.action_confirm()
        picking_receipt.move_lines.quantity_done = 3
        backorder_wiz = picking_receipt.button_validate()
        backorder_wiz = self.env['stock.backorder.confirmation'].browse(
            backorder_wiz['res_id'])
        backorder_wiz.process()
        backorder = self.env['stock.picking'].search([
            ('backorder_id', '=', picking_receipt.id)])
        self.assertTrue(backorder)
        self.assertEqual(backorder.move_lines.product_uom_qty, 2)
        orig_moves = backorder.move_lines.move_orig_ids
        subcontract_order = orig_moves.mapped('production_id').filtered(
            lambda p: p.state != 'done')
        self.assertTrue(subcontract_order)
        self.assertEqual(subcontract_order.product_qty, 5)
        self.assertEqual(subcontract_order.qty_produced, 3)
        backorder.move_lines.quantity_done = 2
        backorder.action_done()
        orig_moves = picking_receipt.move_lines.move_orig_ids
        self.assertTrue(orig_moves.mapped('production_id').state == 'done')

    def test_flow_9(self):
        resupply_sub_on_order_route = self.env['stock.location.route'].search([
            ('name', '=', 'Resupply Subcontractor on Order')
        ])
        (self.comp1 + self.comp2).write({
            'route_ids': [(4, resupply_sub_on_order_route.id)]
        })
        picking_receipt = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'partner_id': self.subcontractor_partner1.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'move_lines': [(0, 0, {
                'name': self.finished.name,
                'product_id': self.finished.id,
                'product_uom_qty': 5,
                'product_uom': self.finished.uom_id.id,
                'location_id': self.env.ref('stock.stock_location_suppliers').id,
                'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            })],
        })
        picking_receipt.action_confirm()
        picking_delivery = self.env['stock.move'].search([
            ('product_id', 'in', (self.comp1 | self.comp2).ids)
        ]).mapped('picking_id')
        self.assertTrue(picking_delivery)
        self.assertEqual(picking_delivery.state, 'confirmed')
        self.assertEqual(self.comp1.virtual_available, -5)
        self.assertEqual(self.comp2.virtual_available, -5)
        picking_receipt.move_lines._action_cancel()
        self.assertEqual(picking_delivery.state, 'cancel')
        self.assertEqual(self.comp1.virtual_available, 0.0)
        self.assertEqual(self.comp1.virtual_available, 0.0)


class TestSubcontractingTracking(TransactionCase):
    def setUp(self):
        super(TestSubcontractingTracking, self).setUp()
        main_company_1 = self.env['res.partner'].create({
            'name': 'main_partner'})
        self.subcontractor_partner1 = self.env['res.partner'].create({
            'name': 'Subcontractor 1',
            'parent_id': main_company_1.id,
            'company_id': self.env.ref('base.main_company').id
        })

        seller = self.env['product.supplierinfo'].create({
            'name': self.subcontractor_partner1.id,
            'price': 10.0,
        })
        self.comp1_sn = self.env['product.product'].create({
            'name': 'Component1',
            'type': 'product',
            'seller_ids': [(6, 0, [seller.id])],
            'categ_id': self.env.ref('product.product_category_all').id,
            'tracking': 'serial'
        })
        self.comp2 = self.env['product.product'].create({
            'name': 'Component2',
            'type': 'product',
            'seller_ids': [(6, 0, [seller.id])],
            'categ_id': self.env.ref('product.product_category_all').id,
        })

        self.finished_lot = self.env['product.product'].create({
            'name': 'finished',
            'type': 'product',
            'categ_id': self.env.ref('product.product_category_all').id,
            'tracking': 'lot'
        })
        self.bom_tracked = self.env['mrp.bom'].create({
            'type': 'subcontract',
            'product_tmpl_id': self.finished_lot.product_tmpl_id.id,
            'subcontractor_ids': [(4, self.subcontractor_partner1.id)],
            'bom_line_ids': [
                (0, 0, {
                    'product_id': self.comp1_sn.id,
                    'product_qty': 1,
                }),
                (0, 0, {
                    'product_id': self.comp2.id,
                    'product_qty': 1,
                }),
            ],
        })

    def test_flow_tracked_1(self):
        picking_receipt = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'partner_id': self.subcontractor_partner1.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'move_lines': [(0, 0, {
                'name': self.finished_lot.name,
                'product_id': self.finished_lot.id,
                'product_uom_qty': 1,
                'product_uom': self.finished_lot.uom_id.id,
                'location_id': self.env.ref('stock.stock_location_suppliers').id,
                'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            })],
        })
        picking_receipt.action_confirm()
        self.assertTrue(picking_receipt.display_action_record_components)
        mo = self.env['mrp.production'].search([
            ('bom_id', '=', self.bom_tracked.id)])
        self.assertEqual(len(mo), 1)
        self.assertEquals(mo.state, 'confirmed')
        wh = picking_receipt.picking_type_id.warehouse_id
        self.assertEquals(mo.picking_type_id, wh.subcontracting_type_id)
        self.assertFalse(mo.picking_type_id.active)
        pg1 = self.env['procurement.group'].create({})
        self.env['stock.warehouse.orderpoint'].create({
            'name': 'xxx',
            'product_id': self.comp1_sn.id,
            'product_min_qty': 0,
            'product_max_qty': 0,
            'location_id': (
                self.env.user.company_id.subcontracting_location_id.id),
            'group_id': pg1.id,
        })
        self.env['procurement.group'].run_scheduler()
        picking = self.env['stock.picking'].search([('group_id', '=', pg1.id)])
        self.assertEqual(len(picking), 1)
        self.assertEquals(picking.picking_type_id, wh.out_type_id)
        lot_id = self.env['stock.production.lot'].create({
            'name': 'lot1',
            'product_id': self.finished_lot.id,
        })
        serial_id = self.env['stock.production.lot'].create({
            'name': 'lot1',
            'product_id': self.comp1_sn.id,
        })
        produce = self.env['mrp.product.produce'].with_context(
            active_id=mo.id,
            active_ids=[mo.id],
        ).create({
            'product_qty': 1.0,
            'lot_id': lot_id.id,
        })
        produce.write({
            'produce_line_ids': [
                (0, 0, {
                    'move_id': mo.move_raw_ids[0].id,
                    'product_id': self.comp1_sn.id,
                    'qty_done': 1.0,
                    'lot_id': serial_id.id,
                }),
            ],
        })
        produce.do_produce()
        self.assertFalse(picking_receipt.display_action_record_components)
        picking_receipt.move_lines.quantity_done = 1
        picking_receipt.move_lines.move_line_ids.lot_id = lot_id.id
        picking_receipt.button_validate()
        self.assertEquals(mo.state, 'done')
        avail_qty_comp1 = self.env['stock.quant']._get_available_quantity(
            self.comp1_sn,
            self.subcontractor_partner1.property_stock_subcontractor,
            allow_negative=True)
        avail_qty_comp2 = self.env['stock.quant']._get_available_quantity(
            self.comp2,
            self.subcontractor_partner1.property_stock_subcontractor,
            allow_negative=True)
        avail_qty_finished = self.env['stock.quant']._get_available_quantity(
            self.finished_lot, wh.lot_stock_id)
        self.assertEquals(avail_qty_comp1, -1)
        self.assertEquals(avail_qty_comp2, -1)
        self.assertEquals(avail_qty_finished, 1)
