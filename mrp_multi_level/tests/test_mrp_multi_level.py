# Copyright 2018-19 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.mrp_multi_level.tests.common import TestMrpMultiLevelCommon
from odoo import fields


class TestMrpMultiLevel(TestMrpMultiLevelCommon):

    def test_01_mrp_levels(self):
        """Tests computation of MRP levels."""
        self.assertEqual(self.fp_1.llc, 0)
        self.assertEqual(self.fp_2.llc, 0)
        self.assertEqual(self.sf_1.llc, 1)
        self.assertEqual(self.sf_2.llc, 1)
        self.assertEqual(self.pp_1.llc, 2)
        self.assertEqual(self.pp_2.llc, 2)

    def test_02_product_mrp_area(self):
        """Tests that mrp products are generated correctly."""
        product_mrp_area = self.product_mrp_area_obj.search([
            ('product_id', '=', self.pp_1.id)])
        self.assertEqual(product_mrp_area.supply_method, 'buy')
        self.assertEqual(product_mrp_area.main_supplier_id, self.vendor)
        self.assertEqual(product_mrp_area.qty_available, 10.0)
        product_mrp_area = self.product_mrp_area_obj.search([
            ('product_id', '=', self.sf_1.id)])
        self.assertEqual(product_mrp_area.supply_method, 'manufacture')

    def test_03_mrp_moves(self):
        """Tests for mrp moves generated."""
        moves = self.mrp_move_obj.search([
            ('product_id', '=', self.pp_1.id),
        ])
        self.assertEqual(len(moves), 3)
        self.assertNotIn('s', moves.mapped('mrp_type'))
        for move in moves:
            self.assertTrue(move.planned_order_up_ids)
            if move.planned_order_up_ids.product_mrp_area_id.product_id == \
                    self.fp_1:
                # Demand coming from FP-1
                self.assertEqual(
                    move.planned_order_up_ids.mrp_action, "manufacture")
                self.assertEqual(move.mrp_qty, -200.0)
            elif move.planned_order_up_ids.product_mrp_area_id.product_id == \
                    self.sf_1:
                # Demand coming from FP-2 -> SF-1
                self.assertEqual(
                    move.planned_order_up_ids.mrp_action, "manufacture")
                if move.mrp_date == self.date_5:
                    self.assertEqual(move.mrp_qty, -90.0)
                elif move.mrp_date == self.date_8:
                    self.assertEqual(move.mrp_qty, -72.0)
        # Check actions:
        planned_orders = self.planned_order_obj.search([
            ('product_id', '=', self.pp_1.id),
        ])
        self.assertEqual(len(planned_orders), 3)
        for plan in planned_orders:
            self.assertEqual(plan.mrp_action, 'buy')
        # Check PP-2 PO being accounted:
        po_move = self.mrp_move_obj.search([
            ('product_id', '=', self.pp_2.id),
            ('mrp_type', '=', 's'),
        ])
        self.assertEqual(len(po_move), 1)
        self.assertEqual(po_move.purchase_order_id, self.po)
        self.assertEqual(po_move.purchase_line_id, self.po.order_line)

    def test_04_mrp_multi_level(self):
        """Tests MRP inventories created."""
        # FP-1
        fp_1_inventory_lines = self.mrp_inventory_obj.search(
            [('product_mrp_area_id.product_id', '=', self.fp_1.id)])
        self.assertEqual(len(fp_1_inventory_lines), 1)
        self.assertEqual(fp_1_inventory_lines.date, self.date_7)
        self.assertEqual(fp_1_inventory_lines.demand_qty, 100.0)
        self.assertEqual(fp_1_inventory_lines.to_procure, 100.0)
        # FP-2
        fp_2_line_1 = self.mrp_inventory_obj.search([
            ('product_mrp_area_id.product_id', '=', self.fp_2.id),
            ('date', '=', self.date_7)])
        self.assertEqual(len(fp_2_line_1), 1)
        self.assertEqual(fp_2_line_1.demand_qty, 15.0)
        self.assertEqual(fp_2_line_1.to_procure, 15.0)
        # TODO: ask odoo to fix it... should be date10
        fp_2_line_2 = self.mrp_inventory_obj.search([
            ('product_mrp_area_id.product_id', '=', self.fp_2.id),
            ('date', '=', self.date_9)])
        self.assertEqual(len(fp_2_line_2), 1)
        self.assertEqual(fp_2_line_2.demand_qty, 0.0)
        self.assertEqual(fp_2_line_2.to_procure, 0.0)
        self.assertEqual(fp_2_line_2.supply_qty, 12.0)

        # SF-1
        sf_1_line_1 = self.mrp_inventory_obj.search([
            ('product_mrp_area_id.product_id', '=', self.sf_1.id),
            ('date', '=', self.date_6)])
        self.assertEqual(len(sf_1_line_1), 1)
        self.assertEqual(sf_1_line_1.demand_qty, 30.0)
        self.assertEqual(sf_1_line_1.to_procure, 30.0)
        sf_1_line_2 = self.mrp_inventory_obj.search([
            ('product_mrp_area_id.product_id', '=', self.sf_1.id),
            ('date', '=', self.date_9)])
        self.assertEqual(len(sf_1_line_2), 1)
        self.assertEqual(sf_1_line_2.demand_qty, 24.0)
        self.assertEqual(sf_1_line_2.to_procure, 24.0)
        # SF-2
        sf_2_line_1 = self.mrp_inventory_obj.search([
            ('product_mrp_area_id.product_id', '=', self.sf_2.id),
            ('date', '=', self.date_6)])
        self.assertEqual(len(sf_2_line_1), 1)
        self.assertEqual(sf_2_line_1.demand_qty, 45.0)
        self.assertEqual(sf_2_line_1.to_procure, 30.0)
        sf_2_line_2 = self.mrp_inventory_obj.search([
            ('product_mrp_area_id.product_id', '=', self.sf_2.id),
            ('date', '=', self.date_9)])
        self.assertEqual(len(sf_2_line_2), 1)
        self.assertEqual(sf_2_line_2.demand_qty, 36.0)
        self.assertEqual(sf_2_line_2.to_procure, 36.0)

        # PP-1
        pp_1_line_1 = self.mrp_inventory_obj.search([
            ('product_mrp_area_id.product_id', '=', self.pp_1.id),
            ('date', '=', self.date_5)])
        self.assertEqual(len(pp_1_line_1), 1)
        self.assertEqual(pp_1_line_1.demand_qty, 290.0)
        self.assertEqual(pp_1_line_1.to_procure, 280.0)
        pp_1_line_2 = self.mrp_inventory_obj.search([
            ('product_mrp_area_id.product_id', '=', self.pp_1.id),
            ('date', '=', self.date_8)])
        self.assertEqual(len(pp_1_line_2), 1)
        self.assertEqual(pp_1_line_2.demand_qty, 72.0)
        self.assertEqual(pp_1_line_2.to_procure, 72.0)
        # PP-2
        pp_2_line_1 = self.mrp_inventory_obj.search([
            ('product_mrp_area_id.product_id', '=', self.pp_2.id),
            ('date', '=', self.date_3)])
        self.assertEqual(len(pp_2_line_1), 1)
        self.assertEqual(pp_2_line_1.demand_qty, 90.0)
        # 90.0 demand - 20.0 on hand - 5.0 on PO = 65.0
        self.assertEqual(pp_2_line_1.to_procure, 65.0)
        pp_2_line_2 = self.mrp_inventory_obj.search([
            ('product_mrp_area_id.product_id', '=', self.pp_2.id),
            ('date', '=', self.date_5)])
        self.assertEqual(len(pp_2_line_2), 1)
        self.assertEqual(pp_2_line_2.demand_qty, 360.0)
        self.assertEqual(pp_2_line_2.to_procure, 360.0)
        pp_2_line_3 = self.mrp_inventory_obj.search([
            ('product_mrp_area_id.product_id', '=', self.pp_2.id),
            ('date', '=', self.date_6)])
        self.assertEqual(len(pp_2_line_3), 1)
        self.assertEqual(pp_2_line_3.demand_qty, 108.0)
        self.assertEqual(pp_2_line_3.to_procure, 108.0)
        pp_2_line_4 = self.mrp_inventory_obj.search([
            ('product_mrp_area_id.product_id', '=', self.pp_2.id),
            ('date', '=', self.date_8)])
        self.assertEqual(len(pp_2_line_4), 1)
        self.assertEqual(pp_2_line_4.demand_qty, 48.0)
        self.assertEqual(pp_2_line_4.to_procure, 48.0)

    def test_05_planned_availability(self):
        """Test planned availability computation."""
        # Running availability for PP-1:
        invs = self.mrp_inventory_obj.search([
            ('product_id', '=', self.pp_1.id)],
            order='date')
        self.assertEqual(len(invs), 2)
        expected = [0.0, 0.0]  # No grouping, lot size nor safety stock.
        self.assertEqual(invs.mapped('running_availability'), expected)

    def test_06_procure_mo(self):
        """Test procurement wizard with MOs."""
        mos = self.mo_obj.search([
            ('product_id', '=', self.fp_1.id)])
        self.assertFalse(mos)
        mrp_inv = self.mrp_inventory_obj.search([
            ('product_mrp_area_id.product_id', '=', self.fp_1.id)])
        self.mrp_inventory_procure_wiz.with_context({
            'active_model': 'mrp.inventory',
            'active_ids': mrp_inv.ids,
            'active_id': mrp_inv.id,
        }).create({}).make_procurement()
        mos = self.mo_obj.search([
            ('product_id', '=', self.fp_1.id)])
        self.assertTrue(mos)
        self.assertEqual(mos.product_qty, 100.0)
        mo_date_start = fields.Date.to_date(mos.date_planned_start)
        self.assertEqual(mo_date_start, self.date_5)

    def test_07_adjust_qty_to_order(self):
        """Test the adjustments made to the qty to procure when minimum,
        maximum order quantities and quantity multiple are set."""
        # minimum order quantity:
        mrp_inv_min = self.mrp_inventory_obj.search([
            ('product_mrp_area_id.product_id', '=', self.prod_min.id)])
        self.assertEqual(mrp_inv_min.to_procure, 50.0)
        # maximum order quantity:
        mrp_inv_max = self.mrp_inventory_obj.search([
            ('product_mrp_area_id.product_id', '=', self.prod_max.id)])
        self.assertEqual(mrp_inv_max.to_procure, 150)
        plans = self.planned_order_obj.search([
            ('product_id', '=', self.prod_max.id),
        ])
        self.assertEqual(len(plans), 2)
        self.assertIn(100.0, plans.mapped('mrp_qty'))
        self.assertIn(50.0, plans.mapped('mrp_qty'))
        # quantity multiple:
        mrp_inv_multiple = self.mrp_inventory_obj.search([
            ('product_mrp_area_id.product_id', '=', self.prod_multiple.id)])
        self.assertEqual(mrp_inv_multiple.to_procure, 125)

    def test_08_group_demand(self):
        """Test demand grouping functionality, `nbr_days`."""
        pickings = self.stock_picking_obj.search([
            ('product_id', '=', self.prod_test.id),
            ('location_id', '=', self.sec_loc.id)])
        self.assertEqual(len(pickings), 5)
        moves = self.mrp_move_obj.search([
            ('product_id', '=', self.prod_test.id),
            ('mrp_area_id', '=', self.secondary_area.id),
        ])
        supply_plans = self.planned_order_obj.search([
            ('product_id', '=', self.prod_test.id),
            ('mrp_area_id', '=', self.secondary_area.id),
        ])
        moves_demand = moves.filtered(lambda m: m.mrp_type == 'd')
        self.assertEqual(len(moves_demand), 5)
        # two groups expected:
        # 1. days 8, 9 and 10.
        # 2. days 20, and 22.
        self.assertEqual(len(supply_plans), 2)
        quantities = supply_plans.mapped('mrp_qty')
        week_1_expected = sum(moves_demand[0:3].mapped('mrp_qty'))
        self.assertIn(abs(week_1_expected), quantities)
        week_2_expected = sum(moves_demand[3:].mapped('mrp_qty'))
        self.assertIn(abs(week_2_expected), quantities)

    def test_09_isolated_mrp_area_run(self):
        """Test running MRP for just one area."""
        self.mrp_multi_level_wiz.sudo(self.mrp_manager).create({
            'mrp_area_ids': [(6, 0, self.secondary_area.ids)],
        }).run_mrp_multi_level()
        this = self.mrp_inventory_obj.search([
            ('mrp_area_id', '=', self.secondary_area.id)], limit=1)
        self.assertTrue(this)
        # Only recently exectued areas should have been created by test user:
        self.assertEqual(this.create_uid, self.mrp_manager)
        prev = self.mrp_inventory_obj.search([
            ('mrp_area_id', '!=', self.secondary_area.id)], limit=1)
        self.assertNotEqual(this.create_uid, prev.create_uid)
