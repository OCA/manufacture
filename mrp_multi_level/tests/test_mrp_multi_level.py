# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo.tests.common import SavepointCase
from odoo import fields
from dateutil.rrule import WEEKLY


class TestMrpMultiLevel(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestMrpMultiLevel, cls).setUpClass()
        cls.mo_obj = cls.env['mrp.production']
        cls.po_obj = cls.env['purchase.order']
        cls.product_obj = cls.env['product.product']
        cls.partner_obj = cls.env['res.partner']
        cls.stock_picking_obj = cls.env['stock.picking']
        cls.estimate_obj = cls.env['stock.demand.estimate']
        cls.mrp_multi_level_wiz = cls.env['mrp.multi.level']
        cls.mrp_inventory_procure_wiz = cls.env['mrp.inventory.procure']
        cls.mrp_inventory_obj = cls.env['mrp.inventory']
        cls.mrp_product_obj = cls.env['mrp.product']
        cls.mrp_move_obj = cls.env['mrp.move']

        cls.fp_1 = cls.env.ref('mrp_multi_level.product_product_fp_1')
        cls.fp_2 = cls.env.ref('mrp_multi_level.product_product_fp_2')
        cls.sf_1 = cls.env.ref('mrp_multi_level.product_product_sf_1')
        cls.sf_2 = cls.env.ref('mrp_multi_level.product_product_sf_2')
        cls.pp_1 = cls.env.ref('mrp_multi_level.product_product_pp_1')
        cls.pp_2 = cls.env.ref('mrp_multi_level.product_product_pp_2')
        cls.vendor = cls.env.ref('mrp_multi_level.res_partner_lazer_tech')
        cls.wh = cls.env.ref('stock.warehouse0')
        cls.stock_location = cls.wh.lot_stock_id
        cls.customer_location = cls.env.ref(
            'stock.stock_location_customers')
        cls.calendar = cls.env.ref('resource.resource_calendar_std')
        # Add calendar to WH:
        cls.wh.calendar_id = cls.calendar

        # Partner:
        vendor1 = cls.partner_obj.create({'name': 'Vendor 1'})

        # Create products:
        route_buy = cls.env.ref('purchase.route_warehouse0_buy').id
        cls.prod_test = cls.product_obj.create({
            'name': 'Test Top Seller',
            'type': 'product',
            'list_price': 150.0,
            'produce_delay': 5.0,
            'route_ids': [(6, 0, [route_buy])],
            'seller_ids': [(0, 0, {'name': vendor1.id, 'price': 20.0})],
        })
        cls.prod_min = cls.product_obj.create({
            'name': 'Product with minimum order qty',
            'type': 'product',
            'list_price': 50.0,
            'route_ids': [(6, 0, [route_buy])],
            'seller_ids': [(0, 0, {'name': vendor1.id, 'price': 10.0})],
            'mrp_minimum_order_qty': 50.0,
            'mrp_maximum_order_qty': 0.0,
            'mrp_qty_multiple': 1.0,
        })
        cls.prod_max = cls.product_obj.create({
            'name': 'Product with maximum order qty',
            'type': 'product',
            'list_price': 50.0,
            'route_ids': [(6, 0, [route_buy])],
            'seller_ids': [(0, 0, {'name': vendor1.id, 'price': 10.0})],
            'mrp_minimum_order_qty': 50.0,
            'mrp_maximum_order_qty': 100.0,
            'mrp_qty_multiple': 1.0,
        })
        cls.prod_multiple = cls.product_obj.create({
            'name': 'Product with qty multiple',
            'type': 'product',
            'list_price': 50.0,
            'route_ids': [(6, 0, [route_buy])],
            'seller_ids': [(0, 0, {'name': vendor1.id, 'price': 10.0})],
            'mrp_minimum_order_qty': 50.0,
            'mrp_maximum_order_qty': 500.0,
            'mrp_qty_multiple': 25.0,
        })

        # Create test picking for FP-1 and FP-2:
        res = cls.calendar.plan_days(7+1, datetime.today())
        date_move = res.date()
        cls.picking_1 = cls.stock_picking_obj.create({
            'picking_type_id': cls.env.ref('stock.picking_type_out').id,
            'location_id': cls.stock_location.id,
            'location_dest_id': cls.customer_location.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move fp-1',
                    'product_id': cls.fp_1.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': cls.fp_1.uom_id.id,
                    'product_uom_qty': 100,
                    'location_id': cls.stock_location.id,
                    'location_dest_id': cls.customer_location.id
                }),
                (0, 0, {
                    'name': 'Test move fp-2',
                    'product_id': cls.fp_2.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': cls.fp_2.uom_id.id,
                    'product_uom_qty': 15,
                    'location_id': cls.stock_location.id,
                    'location_dest_id': cls.customer_location.id
                })]
        })
        cls.picking_1.action_confirm()

        # Create test picking for procure qty adjustment tests:
        cls.picking_2 = cls.stock_picking_obj.create({
            'picking_type_id': cls.env.ref('stock.picking_type_out').id,
            'location_id': cls.stock_location.id,
            'location_dest_id': cls.customer_location.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move prod_min',
                    'product_id': cls.prod_min.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': cls.prod_min.uom_id.id,
                    'product_uom_qty': 16,
                    'location_id': cls.stock_location.id,
                    'location_dest_id': cls.customer_location.id
                }),
                (0, 0, {
                    'name': 'Test move prod_max',
                    'product_id': cls.prod_max.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': cls.prod_max.uom_id.id,
                    'product_uom_qty': 140,
                    'location_id': cls.stock_location.id,
                    'location_dest_id': cls.customer_location.id
                }),
                (0, 0, {
                    'name': 'Test move prod_multiple',
                    'product_id': cls.prod_multiple.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': cls.prod_multiple.uom_id.id,
                    'product_uom_qty': 112,
                    'location_id': cls.stock_location.id,
                    'location_dest_id': cls.customer_location.id
                })]
        })
        cls.picking_2.action_confirm()

        # Create Test PO:
        date_po = cls.calendar.plan_days(1+1, datetime.today()).date()
        cls.po = cls.po_obj.create({
            'name': 'Test PO-001',
            'partner_id': cls.vendor.id,
            'order_line': [
                (0, 0, {
                    'name': 'Test PP-2 line',
                    'product_id': cls.pp_2.id,
                    'date_planned': date_po,
                    'product_qty': 5.0,
                    'product_uom': cls.pp_2.uom_id.id,
                    'price_unit': 25.0,
                })],
        })

        # Create test MO:
        date_mo = cls.calendar.plan_days(9+1, datetime.today()).date()
        bom_fp_2 = cls.env.ref('mrp_multi_level.mrp_bom_fp_2')
        cls.mo = cls.mo_obj.create({
            'product_id': cls.fp_2.id,
            'bom_id': bom_fp_2.id,
            'product_qty': 12.0,
            'product_uom_id': cls.fp_2.uom_id.id,
            'date_planned_start': date_mo,
        })

        # Dates (Strings):
        today = datetime.today()
        cls.date_3 = fields.Date.to_string(
            cls.calendar.plan_days(3+1, datetime.today()).date())
        cls.date_5 = fields.Date.to_string(
            cls.calendar.plan_days(5+1, datetime.today()).date())
        cls.date_6 = fields.Date.to_string(
            cls.calendar.plan_days(6+1, datetime.today()).date())
        cls.date_7 = fields.Date.to_string(
            cls.calendar.plan_days(7+1, datetime.today()).date())
        cls.date_8 = fields.Date.to_string((
            cls.calendar.plan_days(8+1, datetime.today()).date()))
        cls.date_9 = fields.Date.to_string((
            cls.calendar.plan_days(9+1, datetime.today()).date()))
        cls.date_10 = fields.Date.to_string(
            cls.calendar.plan_days(10+1, datetime.today()).date())

        # Create Date Ranges:
        cls.dr_type = cls.env['date.range.type'].create({
            'name': 'Weeks',
            'company_id': False,
            'allow_overlap': False,
        })
        generator = cls.env['date.range.generator'].create({
            'date_start': today - timedelta(days=3),
            'name_prefix': 'W-',
            'type_id': cls.dr_type.id,
            'duration_count': 1,
            'unit_of_time': WEEKLY,
            'count': 3})
        generator.action_apply()

        # Create Demand Estimates:
        ranges = cls.env['date.range'].search(
            [('type_id', '=', cls.dr_type.id)])
        qty = 140.0
        for dr in ranges:
            qty += 70.0
            cls._create_demand_estimate(
                cls.prod_test, cls.stock_location, dr, qty)

        cls.mrp_multi_level_wiz.create({}).run_mrp_multi_level()

    @classmethod
    def _create_demand_estimate(cls, product, location, date_range, qty):
        cls.estimate_obj.create({
            'product_id': product.id,
            'location_id': location.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': qty,
            'date_range_id': date_range.id,
        })

    def test_01_mrp_levels(self):
        """Tests computation of MRP levels."""
        self.assertEqual(self.fp_1.llc, 0)
        self.assertEqual(self.fp_2.llc, 0)
        self.assertEqual(self.sf_1.llc, 1)
        self.assertEqual(self.sf_2.llc, 1)
        self.assertEqual(self.pp_1.llc, 2)
        self.assertEqual(self.pp_2.llc, 2)

    def test_02_mrp_product(self):
        """Tests that mrp products are generated correctly."""
        mrp_product = self.mrp_product_obj.search([
            ('product_id', '=', self.pp_1.id)])
        self.assertEqual(mrp_product.supply_method, 'buy')
        self.assertEqual(mrp_product.main_supplier_id, self.vendor)
        self.assertEqual(mrp_product.mrp_qty_available, 10.0)
        mrp_product = self.mrp_product_obj.search([
            ('product_id', '=', self.sf_1.id)])
        self.assertEqual(mrp_product.supply_method, 'manufacture')

    def test_03_mrp_moves(self):
        """Tests for mrp moves generated."""
        moves = self.mrp_move_obj.search([
            ('product_id', '=', self.pp_1.id),
            ('mrp_action', '=', 'none'),
        ])
        self.assertEqual(len(moves), 3)
        self.assertNotIn('s', moves.mapped('mrp_type'))
        for move in moves:
            self.assertTrue(move.mrp_move_up_ids)
            if move.mrp_move_up_ids.mrp_product_id.product_id == self.fp_1:
                # Demand coming from FP-1
                self.assertEqual(move.mrp_move_up_ids.mrp_action, 'mo')
                self.assertEqual(move.mrp_qty, -200.0)
            elif move.mrp_move_up_ids.mrp_product_id.product_id == self.sf_1:
                # Demand coming from FP-2 -> SF-1
                self.assertEqual(move.mrp_move_up_ids.mrp_action, 'mo')
                if move.mrp_date == self.date_5:
                    self.assertEqual(move.mrp_qty, -90.0)
                elif move.mrp_date == self.date_8:
                    self.assertEqual(move.mrp_qty, -72.0)
        # Check actions:
        moves = self.mrp_move_obj.search([
            ('product_id', '=', self.pp_1.id),
            ('mrp_action', '!=', 'none'),
        ])
        self.assertEqual(len(moves), 3)
        for move in moves:
            self.assertEqual(move.mrp_action, 'po')
            self.assertEqual(move.mrp_type, 's')
        # Check PP-2 PO being accounted:
        po_move = self.mrp_move_obj.search([
            ('product_id', '=', self.pp_2.id),
            ('mrp_action', '=', 'none'),
            ('mrp_type', '=', 's'),
        ])
        self.assertEqual(len(po_move), 1)
        self.assertEqual(po_move.purchase_order_id, self.po)
        self.assertEqual(po_move.purchase_line_id, self.po.order_line)

    def test_04_mrp_multi_level(self):
        """Tests MRP inventories created."""
        # FP-1
        fp_1_inventory_lines = self.mrp_inventory_obj.search(
            [('mrp_product_id.product_id', '=', self.fp_1.id)])
        self.assertEqual(len(fp_1_inventory_lines), 1)
        self.assertEqual(fp_1_inventory_lines.date, self.date_7)
        self.assertEqual(fp_1_inventory_lines.demand_qty, 100.0)
        self.assertEqual(fp_1_inventory_lines.to_procure, 100.0)
        # FP-2
        fp_2_line_1 = self.mrp_inventory_obj.search([
            ('mrp_product_id.product_id', '=', self.fp_2.id),
            ('date', '=', self.date_7)])
        self.assertEqual(len(fp_2_line_1), 1)
        self.assertEqual(fp_2_line_1.demand_qty, 15.0)
        self.assertEqual(fp_2_line_1.to_procure, 15.0)
        # TODO: ask odoo to fix it... should be date10
        fp_2_line_2 = self.mrp_inventory_obj.search([
            ('mrp_product_id.product_id', '=', self.fp_2.id),
            ('date', '=', self.date_9)])
        self.assertEqual(len(fp_2_line_2), 1)
        self.assertEqual(fp_2_line_2.demand_qty, 0.0)
        self.assertEqual(fp_2_line_2.to_procure, 0.0)
        self.assertEqual(fp_2_line_2.supply_qty, 12.0)

        # SF-1
        sf_1_line_1 = self.mrp_inventory_obj.search([
            ('mrp_product_id.product_id', '=', self.sf_1.id),
            ('date', '=', self.date_6)])
        self.assertEqual(len(sf_1_line_1), 1)
        self.assertEqual(sf_1_line_1.demand_qty, 30.0)
        self.assertEqual(sf_1_line_1.to_procure, 30.0)
        sf_1_line_2 = self.mrp_inventory_obj.search([
            ('mrp_product_id.product_id', '=', self.sf_1.id),
            ('date', '=', self.date_9)])
        self.assertEqual(len(sf_1_line_2), 1)
        self.assertEqual(sf_1_line_2.demand_qty, 24.0)
        self.assertEqual(sf_1_line_2.to_procure, 24.0)
        # SF-2
        sf_2_line_1 = self.mrp_inventory_obj.search([
            ('mrp_product_id.product_id', '=', self.sf_2.id),
            ('date', '=', self.date_6)])
        self.assertEqual(len(sf_2_line_1), 1)
        self.assertEqual(sf_2_line_1.demand_qty, 45.0)
        self.assertEqual(sf_2_line_1.to_procure, 30.0)
        sf_2_line_2 = self.mrp_inventory_obj.search([
            ('mrp_product_id.product_id', '=', self.sf_2.id),
            ('date', '=', self.date_9)])
        self.assertEqual(len(sf_2_line_2), 1)
        self.assertEqual(sf_2_line_2.demand_qty, 36.0)
        self.assertEqual(sf_2_line_2.to_procure, 36.0)

        # PP-1
        pp_1_line_1 = self.mrp_inventory_obj.search([
            ('mrp_product_id.product_id', '=', self.pp_1.id),
            ('date', '=', self.date_5)])
        self.assertEqual(len(pp_1_line_1), 1)
        self.assertEqual(pp_1_line_1.demand_qty, 290.0)
        self.assertEqual(pp_1_line_1.to_procure, 280.0)
        pp_1_line_2 = self.mrp_inventory_obj.search([
            ('mrp_product_id.product_id', '=', self.pp_1.id),
            ('date', '=', self.date_8)])
        self.assertEqual(len(pp_1_line_2), 1)
        self.assertEqual(pp_1_line_2.demand_qty, 72.0)
        self.assertEqual(pp_1_line_2.to_procure, 72.0)
        # PP-2
        pp_2_line_1 = self.mrp_inventory_obj.search([
            ('mrp_product_id.product_id', '=', self.pp_2.id),
            ('date', '=', self.date_3)])
        self.assertEqual(len(pp_2_line_1), 1)
        self.assertEqual(pp_2_line_1.demand_qty, 90.0)
        # 90.0 demand - 20.0 on hand - 5.0 on PO = 65.0
        self.assertEqual(pp_2_line_1.to_procure, 65.0)
        pp_2_line_2 = self.mrp_inventory_obj.search([
            ('mrp_product_id.product_id', '=', self.pp_2.id),
            ('date', '=', self.date_5)])
        self.assertEqual(len(pp_2_line_2), 1)
        self.assertEqual(pp_2_line_2.demand_qty, 360.0)
        self.assertEqual(pp_2_line_2.to_procure, 360.0)
        pp_2_line_3 = self.mrp_inventory_obj.search([
            ('mrp_product_id.product_id', '=', self.pp_2.id),
            ('date', '=', self.date_6)])
        self.assertEqual(len(pp_2_line_3), 1)
        self.assertEqual(pp_2_line_3.demand_qty, 108.0)
        self.assertEqual(pp_2_line_3.to_procure, 108.0)
        pp_2_line_4 = self.mrp_inventory_obj.search([
            ('mrp_product_id.product_id', '=', self.pp_2.id),
            ('date', '=', self.date_8)])
        self.assertEqual(len(pp_2_line_4), 1)
        self.assertEqual(pp_2_line_4.demand_qty, 48.0)
        self.assertEqual(pp_2_line_4.to_procure, 48.0)

    def test_05_moves_extra_info(self):
        """Test running availability and actions counters computation on
        mrp moves."""
        # Running availability for PP-1:
        moves = self.mrp_move_obj.search([
            ('product_id', '=', self.pp_1.id)],
            order='mrp_date, mrp_type desc, id')
        self.assertEqual(len(moves), 6)
        expected = [200.0, 290.0, 90.0, 0.0, 72.0, 0.0]
        self.assertEqual(moves.mapped('running_availability'), expected)
        # Actions counters for PP-1:
        mrp_product = self.mrp_product_obj.search([
            ('product_id', '=', self.pp_1.id)
        ])
        self.assertEqual(mrp_product.nbr_mrp_actions, 3)
        self.assertEqual(mrp_product.nbr_mrp_actions_4w, 3)

    def test_06_demand_estimates(self):
        """Tests demand estimates integration."""
        estimates = self.estimate_obj.search(
            [('product_id', '=', self.prod_test.id)])
        self.assertEqual(len(estimates), 3)
        moves = self.mrp_move_obj.search([
            ('product_id', '=', self.prod_test.id),
        ])
        # 3 weeks - 3 days in the past = 18 days of valid estimates:
        moves_from_estimates = moves.filtered(lambda m: m.mrp_type == 'd')
        self.assertEqual(len(moves_from_estimates), 18)
        quantities = moves_from_estimates.mapped('mrp_qty')
        self.assertIn(-30.0, quantities)  # 210 a week => 30.0 dayly:
        self.assertIn(-40.0, quantities)  # 280 a week => 40.0 dayly:
        self.assertIn(-50.0, quantities)  # 350 a week => 50.0 dayly:
        actions = moves.filtered(lambda m: m.mrp_action == 'po')
        self.assertEqual(len(actions), 18)

    def test_07_procure_mo(self):
        """Test procurement wizard with MOs."""
        mos = self.mo_obj.search([
            ('product_id', '=', self.fp_1.id)])
        self.assertFalse(mos)
        mrp_inv = self.mrp_inventory_obj.search([
            ('mrp_product_id.product_id', '=', self.fp_1.id)])
        self.mrp_inventory_procure_wiz.with_context({
            'active_model': 'mrp.inventory',
            'active_ids': mrp_inv.ids,
            'active_id': mrp_inv.id,
        }).create({}).make_procurement()
        mos = self.mo_obj.search([
            ('product_id', '=', self.fp_1.id)])
        self.assertTrue(mos)
        self.assertEqual(mos.product_qty, 100.0)
        mo_date_start = mos.date_planned_start.split(' ')[0]
        self.assertEqual(mo_date_start, self.date_5)

    def test_08_adjust_qty_to_order(self):
        """Test the adjustments made to the qty to procure when minimum,
        maximum order quantities and quantity multiple are set."""
        # minimum order quantity:
        mrp_inv_min = self.mrp_inventory_obj.search([
            ('mrp_product_id.product_id', '=', self.prod_min.id)])
        self.assertEqual(mrp_inv_min.to_procure, 50.0)
        # maximum order quantity:
        mrp_inv_max = self.mrp_inventory_obj.search([
            ('mrp_product_id.product_id', '=', self.prod_max.id)])
        self.assertEqual(mrp_inv_max.to_procure, 150)
        moves = self.mrp_move_obj.search([
            ('product_id', '=', self.prod_max.id),
            ('mrp_action', '!=', 'none'),
        ])
        self.assertEqual(len(moves), 2)
        self.assertIn(100.0, moves.mapped('mrp_qty'))
        self.assertIn(50.0, moves.mapped('mrp_qty'))
        # quantity multiple:
        mrp_inv_multiple = self.mrp_inventory_obj.search([
            ('mrp_product_id.product_id', '=', self.prod_multiple.id)])
        self.assertEqual(mrp_inv_multiple.to_procure, 125)

    # TODO: test procure wizard: pos, multiple...
    # TODO: test multiple destination IDS:...
