# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import date, datetime, timedelta
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import ValidationError

from odoo.addons.purchase_stock.models import stock_rule as purchase_stock_rule

from .common import TestMrpMultiLevelCommon


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
        product_mrp_area = self.product_mrp_area_obj.search(
            [("product_id", "=", self.pp_1.id)]
        )
        self.assertEqual(product_mrp_area.supply_method, "buy")
        self.assertEqual(product_mrp_area.main_supplier_id, self.vendor)
        self.assertEqual(product_mrp_area.qty_available, 10.0)
        product_mrp_area = self.product_mrp_area_obj.search(
            [("product_id", "=", self.sf_1.id)]
        )
        self.assertEqual(product_mrp_area.supply_method, "manufacture")
        self.assertFalse(product_mrp_area.main_supplier_id)
        self.assertFalse(product_mrp_area.main_supplierinfo_id)
        # Archiving the product should archive parameters:
        self.assertTrue(product_mrp_area.active)
        self.sf_1.active = False
        self.assertFalse(product_mrp_area.active)

    def test_03_mrp_moves(self):
        """Tests for mrp moves generated."""
        moves = self.mrp_move_obj.search([("product_id", "=", self.pp_1.id)])
        self.assertEqual(len(moves), 3)
        self.assertNotIn("s", moves.mapped("mrp_type"))
        for move in moves:
            self.assertTrue(move.planned_order_up_ids)
            if move.planned_order_up_ids.product_mrp_area_id.product_id == self.fp_1:
                # Demand coming from FP-1
                self.assertEqual(move.planned_order_up_ids.mrp_action, "manufacture")
                self.assertEqual(move.mrp_qty, -200.0)
            elif move.planned_order_up_ids.product_mrp_area_id.product_id == self.sf_1:
                # Demand coming from FP-2 -> SF-1
                self.assertEqual(move.planned_order_up_ids.mrp_action, "manufacture")
                if move.mrp_date == self.date_5:
                    self.assertEqual(move.mrp_qty, -90.0)
                elif move.mrp_date == self.date_8:
                    self.assertEqual(move.mrp_qty, -72.0)
        # Check actions:
        planned_orders = self.planned_order_obj.search(
            [("product_id", "=", self.pp_1.id)]
        )
        self.assertEqual(len(planned_orders), 3)
        for plan in planned_orders:
            self.assertEqual(plan.mrp_action, "buy")
        # Check PP-2 PO being accounted:
        po_move = self.mrp_move_obj.search(
            [("product_id", "=", self.pp_2.id), ("mrp_type", "=", "s")]
        )
        self.assertEqual(len(po_move), 1)
        self.assertEqual(po_move.purchase_order_id, self.po)
        self.assertEqual(po_move.purchase_line_id, self.po.order_line)

    def test_04_mrp_multi_level(self):
        """Tests MRP inventories created."""
        # FP-1
        fp_1_inventory_lines = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.fp_1.id)]
        )
        self.assertEqual(len(fp_1_inventory_lines), 1)
        self.assertEqual(fp_1_inventory_lines.date, self.date_7)
        self.assertEqual(fp_1_inventory_lines.demand_qty, 100.0)
        self.assertEqual(fp_1_inventory_lines.to_procure, 100.0)
        # FP-2
        fp_2_line_1 = self.mrp_inventory_obj.search(
            [
                ("product_mrp_area_id.product_id", "=", self.fp_2.id),
                ("date", "=", self.date_7),
            ]
        )
        self.assertEqual(len(fp_2_line_1), 1)
        self.assertEqual(fp_2_line_1.demand_qty, 15.0)
        self.assertEqual(fp_2_line_1.to_procure, 15.0)
        fp_2_line_2 = self.mrp_inventory_obj.search(
            [
                ("product_mrp_area_id.product_id", "=", self.fp_2.id),
                ("date", "=", self.date_10),
            ]
        )
        self.assertEqual(len(fp_2_line_2), 1)
        self.assertEqual(fp_2_line_2.demand_qty, 0.0)
        self.assertEqual(fp_2_line_2.to_procure, 0.0)
        self.assertEqual(fp_2_line_2.supply_qty, 12.0)

        # SF-1
        sf_1_line_1 = self.mrp_inventory_obj.search(
            [
                ("product_mrp_area_id.product_id", "=", self.sf_1.id),
                ("date", "=", self.date_6),
            ]
        )
        self.assertEqual(len(sf_1_line_1), 1)
        self.assertEqual(sf_1_line_1.demand_qty, 30.0)
        self.assertEqual(sf_1_line_1.to_procure, 30.0)
        sf_1_line_2 = self.mrp_inventory_obj.search(
            [
                ("product_mrp_area_id.product_id", "=", self.sf_1.id),
                ("date", "=", self.date_9),
            ]
        )
        self.assertEqual(len(sf_1_line_2), 1)
        self.assertEqual(sf_1_line_2.demand_qty, 24.0)
        self.assertEqual(sf_1_line_2.to_procure, 24.0)
        # SF-2
        sf_2_line_1 = self.mrp_inventory_obj.search(
            [
                ("product_mrp_area_id.product_id", "=", self.sf_2.id),
                ("date", "=", self.date_6),
            ]
        )
        self.assertEqual(len(sf_2_line_1), 1)
        self.assertEqual(sf_2_line_1.demand_qty, 45.0)
        self.assertEqual(sf_2_line_1.to_procure, 30.0)
        sf_2_line_2 = self.mrp_inventory_obj.search(
            [
                ("product_mrp_area_id.product_id", "=", self.sf_2.id),
                ("date", "=", self.date_9),
            ]
        )
        self.assertEqual(len(sf_2_line_2), 1)
        self.assertEqual(sf_2_line_2.demand_qty, 36.0)
        self.assertEqual(sf_2_line_2.to_procure, 36.0)

        # PP-1
        pp_1_line_1 = self.mrp_inventory_obj.search(
            [
                ("product_mrp_area_id.product_id", "=", self.pp_1.id),
                ("date", "=", self.date_5),
            ]
        )
        self.assertEqual(len(pp_1_line_1), 1)
        self.assertEqual(pp_1_line_1.demand_qty, 290.0)
        self.assertEqual(pp_1_line_1.to_procure, 280.0)
        pp_1_line_2 = self.mrp_inventory_obj.search(
            [
                ("product_mrp_area_id.product_id", "=", self.pp_1.id),
                ("date", "=", self.date_8),
            ]
        )
        self.assertEqual(len(pp_1_line_2), 1)
        self.assertEqual(pp_1_line_2.demand_qty, 72.0)
        self.assertEqual(pp_1_line_2.to_procure, 72.0)
        # PP-2
        pp_2_line_1 = self.mrp_inventory_obj.search(
            [
                ("product_mrp_area_id.product_id", "=", self.pp_2.id),
                ("date", "=", self.date_3),
            ]
        )
        self.assertEqual(len(pp_2_line_1), 1)
        self.assertEqual(pp_2_line_1.demand_qty, 90.0)
        # 90.0 demand - 20.0 on hand - 5.0 on PO = 65.0
        self.assertEqual(pp_2_line_1.to_procure, 65.0)
        pp_2_line_2 = self.mrp_inventory_obj.search(
            [
                ("product_mrp_area_id.product_id", "=", self.pp_2.id),
                ("date", "=", self.date_5),
            ]
        )
        self.assertEqual(len(pp_2_line_2), 1)
        self.assertEqual(pp_2_line_2.demand_qty, 360.0)
        self.assertEqual(pp_2_line_2.to_procure, 360.0)
        pp_2_line_3 = self.mrp_inventory_obj.search(
            [
                ("product_mrp_area_id.product_id", "=", self.pp_2.id),
                ("date", "=", self.date_6),
            ]
        )
        self.assertEqual(len(pp_2_line_3), 1)
        self.assertEqual(pp_2_line_3.demand_qty, 108.0)
        self.assertEqual(pp_2_line_3.to_procure, 108.0)
        pp_2_line_4 = self.mrp_inventory_obj.search(
            [
                ("product_mrp_area_id.product_id", "=", self.pp_2.id),
                ("date", "=", self.date_8),
            ]
        )
        self.assertEqual(len(pp_2_line_4), 1)
        self.assertEqual(pp_2_line_4.demand_qty, 48.0)
        self.assertEqual(pp_2_line_4.to_procure, 48.0)

    def test_05_planned_availability(self):
        """Test planned availability computation."""
        # Running availability for PP-1:
        invs = self.mrp_inventory_obj.search(
            [("product_id", "=", self.pp_1.id)], order="date"
        )
        self.assertEqual(len(invs), 2)
        expected = [0.0, 0.0]  # No grouping, lot size nor safety stock.
        self.assertEqual(invs.mapped("running_availability"), expected)

    def test_06_procure_mo(self):
        """Test procurement wizard with MOs."""
        mos = self.mo_obj.search([("product_id", "=", self.fp_1.id)])
        self.assertFalse(mos)
        mrp_inv = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.fp_1.id)]
        )
        self.mrp_inventory_procure_wiz.with_context(
            active_model="mrp.inventory",
            active_ids=mrp_inv.ids,
            active_id=mrp_inv.id,
        ).create({}).make_procurement()
        mos = self.mo_obj.search([("product_id", "=", self.fp_1.id)])
        self.assertTrue(mos)
        self.assertEqual(mos.product_qty, 100.0)
        mo_date_start = fields.Date.to_date(mos.date_planned_start)
        self.assertEqual(mo_date_start, self.date_5)

    def test_07_adjust_qty_to_order(self):
        """Test the adjustments made to the qty to procure when minimum,
        maximum order quantities and quantity multiple are set."""
        # minimum order quantity:
        mrp_inv_min = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.prod_min.id)]
        )
        self.assertEqual(mrp_inv_min.to_procure, 50.0)
        # maximum order quantity:
        mrp_inv_max = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.prod_max.id)]
        )
        self.assertEqual(mrp_inv_max.to_procure, 150)
        plans = self.planned_order_obj.search([("product_id", "=", self.prod_max.id)])
        self.assertEqual(len(plans), 2)
        self.assertIn(100.0, plans.mapped("mrp_qty"))
        self.assertIn(50.0, plans.mapped("mrp_qty"))
        # quantity multiple:
        mrp_inv_multiple = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.prod_multiple.id)]
        )
        self.assertEqual(mrp_inv_multiple.to_procure, 125)

    def test_08_group_demand(self):
        """Test demand grouping functionality, `nbr_days`."""
        pickings = self.stock_picking_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("location_id", "=", self.sec_loc.id),
            ]
        )
        self.assertEqual(len(pickings), 5)
        moves = self.mrp_move_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("mrp_area_id", "=", self.secondary_area.id),
            ]
        )
        supply_plans = self.planned_order_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("mrp_area_id", "=", self.secondary_area.id),
            ]
        )
        moves_demand = moves.filtered(lambda m: m.mrp_type == "d")
        self.assertEqual(len(moves_demand), 5)
        # two groups expected:
        # 1. days 8, 9 and 10.
        # 2. days 20, and 22.
        self.assertEqual(len(supply_plans), 2)
        quantities = supply_plans.mapped("mrp_qty")
        week_1_expected = sum(moves_demand[0:3].mapped("mrp_qty"))
        self.assertIn(abs(week_1_expected), quantities)
        week_2_expected = sum(moves_demand[3:].mapped("mrp_qty"))
        self.assertIn(abs(week_2_expected), quantities)

    def test_09_isolated_mrp_area_run(self):
        """Test running MRP for just one area."""
        self.mrp_multi_level_wiz.with_user(self.mrp_manager).create(
            {"mrp_area_ids": [(6, 0, self.secondary_area.ids)]}
        ).run_mrp_multi_level()
        this = self.mrp_inventory_obj.search(
            [("mrp_area_id", "=", self.secondary_area.id)], limit=1
        )
        self.assertTrue(this)
        # Only recently exectued areas should have been created by test user:
        self.assertEqual(this.create_uid, self.mrp_manager)
        prev = self.mrp_inventory_obj.search(
            [("mrp_area_id", "!=", self.secondary_area.id)], limit=1
        )
        self.assertNotEqual(this.create_uid, prev.create_uid)

    def test_11_special_scenario_1(self):
        """When grouping demand supply and demand are in the same day but
        supply goes first."""
        moves = self.mrp_move_obj.search(
            [("product_id", "=", self.product_scenario_1.id)]
        )
        self.assertEqual(len(moves), 4)
        mrp_invs = self.mrp_inventory_obj.search(
            [("product_id", "=", self.product_scenario_1.id)]
        )
        self.assertEqual(len(mrp_invs), 2)
        # Net needs = 124 + 90 - 87 = 127 -> 130 (because of qty multiple)
        self.assertEqual(mrp_invs[0].to_procure, 130)
        # Net needs = 18, available on-hand = 3 -> 15
        self.assertEqual(mrp_invs[1].to_procure, 15)

    def test_12_bom_line_attribute_value_skip(self):
        """Check for the correct demand on components of a product with
        multiple variants"""
        product_4b_demand = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.product_4b.id)]
        )
        self.assertTrue(product_4b_demand)
        self.assertEqual(product_4b_demand.to_procure, 100)
        product_4c_demand = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.product_4c.id)]
        )
        self.assertTrue(product_4c_demand)
        self.assertEqual(product_4c_demand.to_procure, 1)
        # Testing variant BoM
        # Supply of one unit for AV-12 or AV-21
        av_12_supply = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.av_12.id)]
        )
        self.assertEqual(av_12_supply.to_procure, 1.0)
        av_21_supply = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.av_21.id)]
        )
        self.assertEqual(av_21_supply.to_procure, 1.0)
        # Testing template BoM
        # Supply of 150 units for AV-11 and AV-22
        av_11_supply = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.av_11.id)]
        )
        self.assertEqual(av_11_supply.to_procure, 100.0)
        av_22_supply = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.av_22.id)]
        )
        self.assertTrue(av_22_supply.to_procure, 100.0)

    def test_13_timezone_handling(self):
        self.calendar.tz = "Australia/Sydney"  # Oct-Apr/Apr-Oct: UTC+11/UTC+10
        date_move = datetime(2090, 4, 19, 20, 00)  # Apr 20 6/7 am in Sidney
        sidney_date = date(2090, 4, 20)
        self._create_picking_in(
            self.product_tz, 10.0, date_move, location=self.cases_loc
        )
        self.mrp_multi_level_wiz.create(
            {"mrp_area_ids": [(6, 0, self.cases_area.ids)]}
        ).run_mrp_multi_level()
        inventory = self.mrp_inventory_obj.search(
            [
                ("mrp_area_id", "=", self.cases_area.id),
                ("product_id", "=", self.product_tz.id),
            ]
        )
        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory.date, sidney_date)

    def test_14_timezone_not_set(self):
        self.wh.calendar_id = False
        date_move = datetime(2090, 4, 19, 20, 00)
        self._create_picking_in(
            self.product_tz, 10.0, date_move, location=self.cases_loc
        )
        self.mrp_multi_level_wiz.create(
            {"mrp_area_ids": [(6, 0, self.cases_area.ids)]}
        ).run_mrp_multi_level()
        inventory = self.mrp_inventory_obj.search(
            [
                ("mrp_area_id", "=", self.cases_area.id),
                ("product_id", "=", self.product_tz.id),
            ]
        )
        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory.date, date_move.date())

    def test_15_units_case(self):
        """When a product has a different purchase unit of measure than
        the general unit of measure and the supply is coming from an RFQ"""
        prod_uom_test_inventory_lines = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.prod_uom_test.id)]
        )
        self.assertEqual(len(prod_uom_test_inventory_lines), 1)
        self.assertEqual(prod_uom_test_inventory_lines.supply_qty, 12.0)
        # Supply qty has to be 12, a dozen of units are in a RFQ.
        self.assertEqual(prod_uom_test_inventory_lines.rfq_qty, 12.0)
        # check that the action opens the correct RfQ:
        res = prod_uom_test_inventory_lines.action_open_rfqs()
        self.assertEqual(res["res_id"], self.po_uom.id)

    def test_16_phantom_comp_planning(self):
        """
        Phantom components will not appear in MRP Inventory or Planned Orders.
        MRP Parameter will have 'phantom' supply method.
        """
        # SF-3
        sf_3_line_1 = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.sf_3.id)]
        )
        self.assertEqual(len(sf_3_line_1), 0)
        sf_3_planned_order_1 = self.planned_order_obj.search(
            [("product_mrp_area_id.product_id", "=", self.sf_3.id)]
        )
        self.assertEqual(sf_3_planned_order_1.mrp_action, "phantom")
        self.assertEqual(sf_3_planned_order_1.mrp_qty, 10.0)
        # PP-3
        pp_3_line_1 = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.pp_3.id)]
        )
        self.assertEqual(len(pp_3_line_1), 1)
        self.assertEqual(pp_3_line_1.demand_qty, 20.0)
        pp_3_planned_orders = self.planned_order_obj.search(
            [("product_mrp_area_id.product_id", "=", self.pp_3.id)]
        )
        self.assertEqual(len(pp_3_planned_orders), 2)
        # PP-4
        pp_4_line_1 = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.pp_4.id)]
        )
        self.assertEqual(len(pp_4_line_1), 1)
        self.assertEqual(pp_4_line_1.demand_qty, 30.0)
        pp_4_planned_orders = self.planned_order_obj.search(
            [("product_mrp_area_id.product_id", "=", self.pp_4.id)]
        )
        self.assertEqual(len(pp_4_planned_orders), 1)

    def test_17_supply_method(self):
        """Test supply method computation."""
        self.fp_4.route_ids = [(5, 0, 0)]
        product_mrp_area = self.product_mrp_area_obj.search(
            [("product_id", "=", self.fp_4.id)]
        )
        self.assertEqual(product_mrp_area.supply_method, "none")
        self.fp_4.route_ids = [(4, self.env.ref("stock.route_warehouse0_mto").id)]
        product_mrp_area._compute_supply_method()
        self.assertEqual(product_mrp_area.supply_method, "pull")
        self.fp_4.route_ids = [(4, self.env.ref("mrp.route_warehouse0_manufacture").id)]
        product_mrp_area._compute_supply_method()
        self.assertEqual(product_mrp_area.supply_method, "manufacture")
        self.fp_4.route_ids = [
            (4, self.env.ref("purchase_stock.route_warehouse0_buy").id)
        ]
        product_mrp_area._compute_supply_method()
        self.assertEqual(product_mrp_area.supply_method, "buy")
        kit_bom = self.mrp_bom_obj.create(
            {
                "product_tmpl_id": self.fp_4.product_tmpl_id.id,
                "product_id": self.fp_4.id,
                "type": "phantom",
            }
        )
        product_mrp_area._compute_supply_method()
        self.assertEqual(product_mrp_area.supply_method, "phantom")
        self.assertEqual(product_mrp_area.supply_bom_id, kit_bom)

    def test_18_priorize_safety_stock(self):
        now = datetime.now()
        product = self.prod_test  # has Buy route
        product.seller_ids[0].delay = 2  # set a purchase lead time
        self.quant_obj._update_available_quantity(product, self.cases_loc, 5)
        self.product_mrp_area_obj.create(
            {
                "product_id": product.id,
                "mrp_area_id": self.cases_area.id,
                "mrp_minimum_stock": 15,
                "mrp_applicable": True,  # needed?
            }
        )
        self._create_picking_out(
            product, 6.0, now + timedelta(days=3), location=self.cases_loc
        )
        self._create_picking_in(
            product, 10.0, now + timedelta(days=7), location=self.cases_loc
        )
        self._create_picking_out(
            product, 12.0, now + timedelta(days=14), location=self.cases_loc
        )
        self.mrp_multi_level_wiz.create(
            {"mrp_area_ids": [(6, 0, self.cases_area.ids)]}
        ).run_mrp_multi_level()
        inventory = self.mrp_inventory_obj.search(
            [
                ("mrp_area_id", "=", self.cases_area.id),
                ("product_id", "=", product.id),
            ]
        )
        expected = [
            {
                "date": now.date(),
                "demand_qty": 0.0,
                "final_on_hand_qty": 5.0,
                "initial_on_hand_qty": 5.0,
                "running_availability": 15.0,
                "supply_qty": 0.0,
                "to_procure": 10.0,
            },
            {
                "date": now.date() + timedelta(days=3),
                "demand_qty": 6.0,
                "final_on_hand_qty": -1.0,
                "initial_on_hand_qty": 5.0,
                "running_availability": 15.0,
                "supply_qty": 0.0,
                "to_procure": 6.0,
            },
            {
                "date": now.date() + timedelta(days=7),
                "demand_qty": 0.0,
                "final_on_hand_qty": 9.0,
                "initial_on_hand_qty": -1.0,
                "running_availability": 25.0,
                "supply_qty": 10.0,
                "to_procure": 0.0,
            },
            {
                "date": now.date() + timedelta(days=14),
                "demand_qty": 12.0,
                "final_on_hand_qty": -3.0,
                "initial_on_hand_qty": 9.0,
                "running_availability": 15.0,
                "supply_qty": 0.0,
                "to_procure": 2.0,
            },
        ]
        self.assertEqual(len(expected), len(inventory))
        for test_vals, inv in zip(expected, inventory):
            for key in test_vals:
                self.assertEqual(
                    test_vals[key],
                    inv[key],
                    f"unexpected value for {key}: {inv[key]} "
                    f"(expected {test_vals[key]} on {inv.date})",
                )

    def test_19_on_hand_with_lots(self):
        """Check that on-hand is correctly computed when tracking by lots."""
        lots_line_1 = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.product_lots.id)]
        )
        self.assertEqual(len(lots_line_1), 1)
        self.assertEqual(lots_line_1.initial_on_hand_qty, 210)
        self.assertEqual(lots_line_1.final_on_hand_qty, 185)

    def test_20_prioritize_safety_stock_grouped_1(self):
        """Test grouped demand MRP but with a short nbr days.
        Safety stock should be ordered."""
        now = datetime.now()
        product = self.prod_test  # has Buy route
        product.seller_ids[0].delay = 2  # set a purchase lead time
        self.quant_obj._update_available_quantity(product, self.cases_loc, 5)
        self.product_mrp_area_obj.create(
            {
                "product_id": product.id,
                "mrp_area_id": self.cases_area.id,
                "mrp_minimum_stock": 15,
                "mrp_nbr_days": 2,
            }
        )
        self._create_picking_out(
            product, 6.0, now + timedelta(days=3), location=self.cases_loc
        )
        self._create_picking_in(
            product, 10.0, now + timedelta(days=7), location=self.cases_loc
        )
        self._create_picking_out(
            product, 12.0, now + timedelta(days=14), location=self.cases_loc
        )
        self.mrp_multi_level_wiz.create(
            {"mrp_area_ids": [(6, 0, self.cases_area.ids)]}
        ).run_mrp_multi_level()
        inventory = self.mrp_inventory_obj.search(
            [
                ("mrp_area_id", "=", self.cases_area.id),
                ("product_id", "=", product.id),
            ]
        )
        expected = [
            {
                "date": now.date(),
                "demand_qty": 0.0,
                "final_on_hand_qty": 5.0,
                "initial_on_hand_qty": 5.0,
                "running_availability": 15.0,
                "supply_qty": 0.0,
                "to_procure": 10.0,
            },
            {
                "date": now.date() + timedelta(days=3),
                "demand_qty": 6.0,
                "final_on_hand_qty": -1.0,
                "initial_on_hand_qty": 5.0,
                "running_availability": 15.0,
                "supply_qty": 0.0,
                "to_procure": 6.0,
            },
            {
                "date": now.date() + timedelta(days=7),
                "demand_qty": 0.0,
                "final_on_hand_qty": 9.0,
                "initial_on_hand_qty": -1.0,
                "running_availability": 25.0,
                "supply_qty": 10.0,
                "to_procure": 0.0,
            },
            {
                "date": now.date() + timedelta(days=14),
                "demand_qty": 12.0,
                "final_on_hand_qty": -3.0,
                "initial_on_hand_qty": 9.0,
                "running_availability": 15.0,
                "supply_qty": 0.0,
                "to_procure": 2.0,
            },
        ]
        self.assertEqual(len(expected), len(inventory))
        for test_vals, inv in zip(expected, inventory):
            for key in test_vals:
                self.assertEqual(
                    test_vals[key],
                    inv[key],
                    f"unexpected value for {key}: {inv[key]} "
                    f"(expected {test_vals[key]} on {inv.date})",
                )

    def test_21_prioritize_safety_stock_grouped_2(self):
        """Test grouped demand MRP but with a longer nbr days.
        Safety stock should be ordered."""
        now = datetime.now()
        product = self.prod_test  # has Buy route
        product.seller_ids[0].delay = 2  # set a purchase lead time
        self.quant_obj._update_available_quantity(product, self.cases_loc, 5)
        self.product_mrp_area_obj.create(
            {
                "product_id": product.id,
                "mrp_area_id": self.cases_area.id,
                "mrp_minimum_stock": 15,
                "mrp_nbr_days": 7,
            }
        )
        self._create_picking_out(
            product, 6.0, now + timedelta(days=3), location=self.cases_loc
        )
        self._create_picking_in(
            product, 10.0, now + timedelta(days=7), location=self.cases_loc
        )
        self._create_picking_out(
            product, 12.0, now + timedelta(days=12), location=self.cases_loc
        )
        self.mrp_multi_level_wiz.create(
            {"mrp_area_ids": [(6, 0, self.cases_area.ids)]}
        ).run_mrp_multi_level()
        inventory = self.mrp_inventory_obj.search(
            [
                ("mrp_area_id", "=", self.cases_area.id),
                ("product_id", "=", product.id),
            ]
        )
        expected = [
            {
                "date": now.date(),
                "demand_qty": 0.0,
                "final_on_hand_qty": 5.0,
                "initial_on_hand_qty": 5.0,
                "running_availability": 21.0,
                "supply_qty": 0.0,
                "to_procure": 16.0,
            },
            {
                "date": now.date() + timedelta(days=3),
                "demand_qty": 6.0,
                "final_on_hand_qty": -1.0,
                "initial_on_hand_qty": 5.0,
                "running_availability": 15.0,
                "supply_qty": 0.0,
                "to_procure": 0.0,
            },
            {
                "date": now.date() + timedelta(days=7),
                "demand_qty": 0.0,
                "final_on_hand_qty": 9.0,
                "initial_on_hand_qty": -1.0,
                "running_availability": 27.0,
                "supply_qty": 10.0,
                "to_procure": 2.0,
            },
            {
                "date": now.date() + timedelta(days=12),
                "demand_qty": 12.0,
                "final_on_hand_qty": -3.0,
                "initial_on_hand_qty": 9.0,
                "running_availability": 15.0,
                "supply_qty": 0.0,
                "to_procure": 0.0,
            },
        ]
        self.assertEqual(len(expected), len(inventory))
        for test_vals, inv in zip(expected, inventory):
            for key in test_vals:
                self.assertEqual(
                    test_vals[key],
                    inv[key],
                    f"unexpected value for {key}: {inv[key]} "
                    f"(expected {test_vals[key]} on {inv.date})",
                )

    def test_22_prioritize_safety_stock_grouped_3(self):
        """Test grouped demand MRP but with an existing incoming supply
        Safety stock should NOT be ordered."""
        now = datetime.now()
        product = self.prod_test  # has Buy route
        product.seller_ids[0].delay = 2  # set a purchase lead time
        self.quant_obj._update_available_quantity(product, self.cases_loc, 5)
        self.product_mrp_area_obj.create(
            {
                "product_id": product.id,
                "mrp_area_id": self.cases_area.id,
                "mrp_minimum_stock": 15,
                "mrp_nbr_days": 7,
            }
        )
        self._create_picking_in(
            product, 30.0, now + timedelta(days=3), location=self.cases_loc
        )
        self._create_picking_out(
            product, 6.0, now + timedelta(days=7), location=self.cases_loc
        )
        self._create_picking_out(
            product, 12.0, now + timedelta(days=12), location=self.cases_loc
        )
        self.mrp_multi_level_wiz.create(
            {"mrp_area_ids": [(6, 0, self.cases_area.ids)]}
        ).run_mrp_multi_level()
        inventory = self.mrp_inventory_obj.search(
            [
                ("mrp_area_id", "=", self.cases_area.id),
                ("product_id", "=", product.id),
            ]
        )
        expected = [
            {
                "date": now.date() + timedelta(days=3),
                "demand_qty": 0.0,
                "initial_on_hand_qty": 5.0,
                "final_on_hand_qty": 35.0,
                "running_availability": 35.0,
                "supply_qty": 30.0,
                "to_procure": 0.0,
            },
            {
                "date": now.date() + timedelta(days=7),
                "demand_qty": 6.0,
                "initial_on_hand_qty": 35.0,
                "final_on_hand_qty": 29.0,
                "running_availability": 29.0,
                "supply_qty": 0.0,
                "to_procure": 0.0,
            },
            {
                "date": now.date() + timedelta(days=12),
                "demand_qty": 12.0,
                "initial_on_hand_qty": 29.0,
                "final_on_hand_qty": 17.0,
                "running_availability": 17.0,
                "supply_qty": 0.0,
                "to_procure": 0.0,
            },
        ]
        self.assertEqual(len(expected), len(inventory))
        for test_vals, inv in zip(expected, inventory):
            for key in test_vals:
                self.assertEqual(
                    test_vals[key],
                    inv[key],
                    f"unexpected value for {key}: {inv[key]} "
                    f"(expected {test_vals[key]} on {inv.date})",
                )

    def test_23_prioritize_safety_stock_with_mrp_moves_today(self):
        """Test MRP but with moves today. Safety stock should not be ordered."""
        now = datetime.now()
        product = self.prod_test  # has Buy route
        product.seller_ids[0].delay = 2  # set a purchase lead time
        self.quant_obj._update_available_quantity(product, self.cases_loc, 5)
        self.product_mrp_area_obj.create(
            {
                "product_id": product.id,
                "mrp_area_id": self.cases_area.id,
                "mrp_minimum_stock": 15,
            }
        )
        self._create_picking_out(product, 10.0, now, location=self.cases_loc)
        self._create_picking_in(product, 20.0, now, location=self.cases_loc)
        self.mrp_multi_level_wiz.create(
            {"mrp_area_ids": [(6, 0, self.cases_area.ids)]}
        ).run_mrp_multi_level()
        inventory = self.mrp_inventory_obj.search(
            [("mrp_area_id", "=", self.cases_area.id), ("product_id", "=", product.id)]
        )
        expected = [
            {
                "date": now.date(),
                "demand_qty": 10.0,
                "final_on_hand_qty": 15.0,
                "initial_on_hand_qty": 5.0,
                "running_availability": 15.0,
                "supply_qty": 20.0,
                "to_procure": 0.0,
            },
        ]
        self.assertEqual(len(expected), len(inventory))
        for test_vals, inv in zip(expected, inventory):
            for key in test_vals:
                self.assertEqual(
                    test_vals[key],
                    inv[key],
                    f"unexpected value for {key}: {inv[key]} "
                    f"(expected {test_vals[key]} on {inv.date})",
                )

    def test_24_prioritize_safety_stock_with_mrp_moves_today_grouped(self):
        """Test grouped demand MRP but with moves today. Safety stock should not be ordered."""
        now = datetime.now()
        product = self.prod_test  # has Buy route
        product.seller_ids[0].delay = 2  # set a purchase lead time
        self.quant_obj._update_available_quantity(product, self.cases_loc, 5)
        self.product_mrp_area_obj.create(
            {
                "product_id": product.id,
                "mrp_area_id": self.cases_area.id,
                "mrp_minimum_stock": 15,
                "mrp_nbr_days": 2,
            }
        )
        self._create_picking_out(product, 10.0, now, location=self.cases_loc)
        self._create_picking_in(product, 20.0, now, location=self.cases_loc)
        self.mrp_multi_level_wiz.create(
            {"mrp_area_ids": [(6, 0, self.cases_area.ids)]}
        ).run_mrp_multi_level()
        inventory = self.mrp_inventory_obj.search(
            [("mrp_area_id", "=", self.cases_area.id), ("product_id", "=", product.id)]
        )
        expected = [
            {
                "date": now.date(),
                "demand_qty": 10.0,
                "final_on_hand_qty": 15.0,
                "initial_on_hand_qty": 5.0,
                "running_availability": 15.0,
                "supply_qty": 20.0,
                "to_procure": 0.0,
            },
        ]
        self.assertEqual(len(expected), len(inventory))
        for test_vals, inv in zip(expected, inventory):
            for key in test_vals:
                self.assertEqual(
                    test_vals[key],
                    inv[key],
                    f"unexpected value for {key}: {inv[key]} "
                    f"(expected {test_vals[key]} on {inv.date})",
                )

    def test_25_phantom_comp_on_hand(self):
        """
        A phantom product with positive qty_available (which is computed from the
        availability of its components) should not satisfy demand, because this leads
        to double counting qty_available of its component products.
        """
        quant = self.quant_obj.sudo().create(
            {
                "product_id": self.pp_3.id,
                "inventory_quantity": 10.0,
                "location_id": self.stock_location.id,
            }
        )
        quant.action_apply_inventory()
        quant = self.quant_obj.sudo().create(
            {
                "product_id": self.pp_4.id,
                "inventory_quantity": 30.0,
                "location_id": self.stock_location.id,
            }
        )
        quant.action_apply_inventory()
        self.assertEqual(self.sf_3.qty_available, 10.0)
        self.mrp_multi_level_wiz.create({}).run_mrp_multi_level()
        # PP-3
        pp_3_line_1 = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.pp_3.id)]
        )
        self.assertEqual(len(pp_3_line_1), 1)
        self.assertEqual(pp_3_line_1.demand_qty, 20.0)
        self.assertEqual(pp_3_line_1.to_procure, 10.0)
        pp_3_planned_orders = self.planned_order_obj.search(
            [("product_mrp_area_id.product_id", "=", self.pp_3.id)]
        )
        self.assertEqual(len(pp_3_planned_orders), 1)
        self.assertEqual(pp_3_planned_orders.mrp_qty, 10)
        sf3_planned_orders = self.env["mrp.planned.order"].search(
            [("product_id", "=", self.sf_3.id)]
        )
        self.assertEqual(len(sf3_planned_orders), 1)
        # Trying to procure a kit planned order will have no effect.
        procure_wizard = (
            self.env["mrp.inventory.procure"]
            .with_context(
                active_model="mrp.planned.order", active_ids=sf3_planned_orders.ids
            )
            .create({})
        )
        self.assertEqual(len(procure_wizard.item_ids), 0)

    def test_26_procure_wizard_mrp_action_override_to_buy(self):
        """Test override to 'buy' creates PO with correct data and
        updates planned_order."""
        mrp_inv = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.fp_1.id)], limit=1
        )
        self.assertTrue(mrp_inv, "No MRP inventory found for FP-1")

        # Get planned order and save initial qty_released
        planned_order = mrp_inv.planned_order_ids.filtered(
            lambda x: x.qty_released < x.mrp_qty
        )[:1]
        self.assertTrue(planned_order, "No planned order with pending qty")
        qty_released_before = planned_order.qty_released

        self.fp_1.write(
            {
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self.vendor.id,
                            "min_qty": 0.0,
                            "price": 10.0,
                            "delay": 1,
                        },
                    )
                ]
            }
        )

        self.mo_obj.search([("product_id", "=", self.fp_1.id)]).unlink()
        before_po_count = self.po_obj.search_count(
            [("company_id", "=", self.company.id)]
        )

        wiz = self.mrp_inventory_procure_wiz.with_context(
            active_model="mrp.inventory",
            active_ids=mrp_inv.ids,
            active_id=mrp_inv.id,
        ).create({})
        self.assertTrue(wiz.item_ids)

        item = wiz.item_ids[0]
        item_qty = item.qty

        item.write({"mrp_action": "buy"})
        wiz.make_procurement()

        mos = self.mo_obj.search([("product_id", "=", self.fp_1.id)])
        self.assertFalse(mos, "No MO should be created for 'buy' action")

        after_po_count = self.po_obj.search_count(
            [("company_id", "=", self.company.id)]
        )
        self.assertGreater(after_po_count, before_po_count, "PO should be created")

        po = self.po_obj.search(
            [
                ("partner_id", "=", self.vendor.id),
                ("order_line.product_id", "=", self.fp_1.id),
            ],
            order="id desc",
            limit=1,
        )
        self.assertTrue(po, "PO with correct vendor and product should exist")

        po_line = po.order_line.filtered(lambda l: l.product_id == self.fp_1)
        self.assertTrue(po_line, "PO should have line for FP-1")
        self.assertEqual(
            po_line.product_qty, item_qty, f"PO line qty should be {item_qty}"
        )
        self.assertEqual(
            po_line.product_uom, self.fp_1.uom_id, "PO line should use product UoM"
        )

        self.assertEqual(
            planned_order.qty_released,
            qty_released_before + item_qty,
            "qty_released MUST increase - order must be marked as released",
        )

    def test_27_procure_wizard_onchange_sets_vendor_currency(self):
        """Onchange purchase defaults should set supplier and currency."""
        planned = self.planned_order_obj.search(
            [("product_id", "=", self.pp_1.id)], limit=1
        )
        self.assertTrue(planned)

        wiz = self.mrp_inventory_procure_wiz.with_context(
            active_model="mrp.planned.order",
            active_ids=planned.ids,
            active_id=planned.id,
        ).create({})
        self.assertTrue(wiz.item_ids)
        item = wiz.item_ids[0]

        item.mrp_action = "buy"
        item._onchange_purchase_defaults()

        self.assertEqual(item.mrp_action, "buy")
        self.assertTrue(item.supplier_id)
        self.assertTrue(item.currency_id)

    def test_28_stock_rule_make_po_domain_and_prepare_po_currency(self):
        usd = self.env.ref("base.USD")
        rule = self.env["stock.rule"].search([], limit=1)
        self.assertTrue(rule)

        dom = rule._make_po_get_domain(
            self.company, {"currency_id": usd.id}, self.vendor
        )
        self.assertIsInstance(dom, tuple)
        self.assertIn(("currency_id", "=", usd.id), dom)
        supplierinfo = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.vendor.id,
                "product_tmpl_id": self.pp_1.product_tmpl_id.id,
                "min_qty": 0.0,
                "price": 10.0,
                "delay": 1,
            }
        )
        po_vals = rule._prepare_purchase_order(
            self.company,
            ["MRP: TEST"],
            [
                {
                    "currency_id": usd.id,
                    "date_planned": fields.Datetime.now(),
                    "supplier": supplierinfo,
                }
            ],
        )
        self.assertEqual(po_vals.get("currency_id"), usd.id)

    def test_29_procure_item_onchange_uom_planned_order(self):
        """Onchange UoM: when source is a planned order, restore the original qty."""
        planned = self.planned_order_obj.search(
            [("product_id", "=", self.pp_1.id)], limit=1
        )
        self.assertTrue(planned)

        wiz = self.mrp_inventory_procure_wiz.with_context(
            active_model="mrp.planned.order",
            active_ids=planned.ids,
            active_id=planned.id,
        ).create({})
        self.assertTrue(wiz.item_ids)
        item = wiz.item_ids[0]

        item.write(
            {
                "source_context": "planned_order",
                "original_qty": 5.0,
                "qty": 0.0,
                "uom_id": self.ref("uom.product_uom_unit"),
            }
        )
        item.onchange_uom_id()
        self.assertEqual(item.qty, 5.0)

    def test_30_procure_item_onchange_uom_inventory_to_procure(self):
        """Onchange UoM: when source is inventory, default qty from `to_procure`."""
        mrp_inv = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.fp_1.id)], limit=1
        )
        self.assertTrue(mrp_inv)

        wiz = self.mrp_inventory_procure_wiz.with_context(
            active_model="mrp.inventory",
            active_ids=mrp_inv.ids,
            active_id=mrp_inv.id,
        ).create({})
        self.assertTrue(wiz.item_ids)
        item = wiz.item_ids[0]

        item.write(
            {
                "source_context": "inventory",
                "original_qty": 0.0,
                "qty": 0.0,
                "uom_id": self.ref("uom.product_uom_unit"),
            }
        )
        mrp_inv.write({"to_procure": 3.0})

        item.onchange_uom_id()
        self.assertEqual(item.qty, 3.0)

    def test_31_get_rule_respects_mrp_action(self):
        """Test that _get_rule returns rule matching mrp_action when provided."""
        mrp_inv = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.fp_1.id)], limit=1
        )
        self.assertTrue(mrp_inv)
        wiz = self.mrp_inventory_procure_wiz.with_context(
            active_model="mrp.inventory",
            active_ids=mrp_inv.ids,
            active_id=mrp_inv.id,
        ).create({})
        self.assertTrue(wiz.item_ids)
        item = wiz.item_ids[0]
        route = self.env["stock.route"].create(
            {
                "name": "Test route (mrp_multi_level)",
                "product_selectable": False,
                "warehouse_selectable": False,
                "company_id": self.company.id,
            }
        )
        picking_type = item.warehouse_id.in_type_id
        pull_rule = self.env["stock.rule"].create(
            {
                "name": "Test pull rule (mrp_multi_level)",
                "route_id": route.id,
                "action": "pull",
                "location_src_id": self.supplier_location.id,
                "location_dest_id": item.location_id.id,
                "picking_type_id": picking_type.id,
                "company_id": self.company.id,
            }
        )
        # Veriffy  _get_rule returns pull rule when mrp_action='pull'
        pg = self.env["procurement.group"]
        values = {
            "mrp_action": "pull",
            "company_id": self.company,
            "warehouse_id": item.warehouse_id,
        }
        found_rule = pg._get_rule(item.product_id, item.location_id, values)
        self.assertEqual(found_rule.id, pull_rule.id)
        self.assertEqual(found_rule.action, "pull")

    def test_32_procure_item_onchange_uom_fallback_original_qty(self):
        """Onchange UoM: when no context, fallback to original qty."""
        planned = self.planned_order_obj.search(
            [("product_id", "=", self.pp_1.id)], limit=1
        )
        self.assertTrue(planned)

        wiz = self.mrp_inventory_procure_wiz.with_context(
            active_model="mrp.planned.order",
            active_ids=planned.ids,
            active_id=planned.id,
        ).create({})
        self.assertTrue(wiz.item_ids)
        item = wiz.item_ids[0]

        item.write(
            {
                "source_context": "inventory",
                "mrp_inventory_id": False,
                "original_qty": 7.0,
                "qty": 0.0,
                "uom_id": self.ref("uom.product_uom_unit"),
            }
        )
        item.onchange_uom_id()
        self.assertEqual(item.qty, 7.0)

    def test_33_procure_wizard_mrp_action_override_to_manufacture(self):
        """Test override to 'manufacture' creates MO with correct data and
        updates planned_order."""
        # Use PP-1 which has supply_method='buy' but we will override to manufacture
        # First we need to create a BOM for PP-1
        bom = self.mrp_bom_obj.create(
            {
                "product_tmpl_id": self.pp_1.product_tmpl_id.id,
                "product_id": self.pp_1.id,
                "type": "normal",
                "product_qty": 1.0,
            }
        )
        self.assertTrue(bom)
        self.assertEqual(bom.product_id, self.pp_1)
        mrp_inv = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.pp_1.id)], limit=1
        )
        self.assertTrue(mrp_inv, "No MRP inventory found for PP-1")

        planned_order = mrp_inv.planned_order_ids.filtered(
            lambda x: x.qty_released < x.mrp_qty
        )[:1]
        self.assertTrue(planned_order, "No planned order with pending qty")
        qty_released_before = planned_order.qty_released

        before_mo_count = self.mo_obj.search_count([("product_id", "=", self.pp_1.id)])

        wiz = self.mrp_inventory_procure_wiz.with_context(
            active_model="mrp.inventory",
            active_ids=mrp_inv.ids,
            active_id=mrp_inv.id,
        ).create({})
        self.assertTrue(wiz.item_ids)

        item = wiz.item_ids[0]
        item_qty = item.qty

        # Override to manufacture (PP-1 normally uses 'buy')
        item.write({"mrp_action": "manufacture"})
        wiz.make_procurement()

        after_mo_count = self.mo_obj.search_count([("product_id", "=", self.pp_1.id)])
        self.assertGreater(
            after_mo_count,
            before_mo_count,
            "A Manufacturing Order should have been created",
        )

        mo = self.mo_obj.search(
            [
                ("product_id", "=", self.pp_1.id),
            ],
            order="id desc",
            limit=1,
        )
        self.assertTrue(mo, "Manufacturing Order should exist")
        self.assertEqual(mo.product_id, self.pp_1, "MO should have correct product")
        self.assertEqual(mo.product_qty, item_qty, f"MO qty should be {item_qty}")
        self.assertEqual(mo.bom_id, bom, "MO should use created BOM")
        self.assertEqual(
            mo.product_uom_id, self.pp_1.uom_id, "MO should use product UoM"
        )

        self.assertEqual(
            planned_order.qty_released,
            qty_released_before + item_qty,
            "qty_released MUST increase - order must be marked as released",
        )

    def test_34_procure_wizard_mrp_action_override_to_pull(self):
        """Test override to 'pull' creates picking with correct data and
        updates planned_order."""
        # Use FP-1 which has supply_method='manufacture' but we will override to pull
        mrp_inv = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.fp_1.id)], limit=1
        )
        self.assertTrue(mrp_inv, "No MRP inventory found for FP-1")

        # Get planned order and save initial qty_released
        planned_order = mrp_inv.planned_order_ids.filtered(
            lambda x: x.qty_released < x.mrp_qty
        )[:1]
        self.assertTrue(planned_order, "No planned order with pending qty")
        qty_released_before = planned_order.qty_released

        wiz = self.mrp_inventory_procure_wiz.with_context(
            active_model="mrp.inventory",
            active_ids=mrp_inv.ids,
            active_id=mrp_inv.id,
        ).create({})
        self.assertTrue(wiz.item_ids)
        item = wiz.item_ids[0]
        item_qty = item.qty

        # Create a pull rule for this location
        route = self.env["stock.route"].create(
            {
                "name": "Test route for pull (test_34)",
                "product_selectable": False,
                "warehouse_selectable": False,
                "company_id": self.company.id,
            }
        )
        picking_type = item.warehouse_id.int_type_id
        pull_rule = self.env["stock.rule"].create(
            {
                "name": "Test pull rule (test_34)",
                "route_id": route.id,
                "action": "pull",
                "location_src_id": self.supplier_location.id,
                "location_dest_id": item.location_id.id,
                "picking_type_id": picking_type.id,
                "company_id": self.company.id,
                "procure_method": "make_to_stock",
            }
        )
        self.assertTrue(pull_rule)
        self.assertEqual(pull_rule.action, "pull")
        # Count existing pickings and MOs for this product
        before_picking_count = self.stock_picking_obj.search_count(
            [
                ("move_ids.product_id", "=", self.fp_1.id),
                ("picking_type_id", "=", picking_type.id),
            ]
        )
        # Clear any existing MOs for FP-1 to avoid confusion
        self.mo_obj.search([("product_id", "=", self.fp_1.id)]).unlink()
        before_mo_count = self.mo_obj.search_count([("product_id", "=", self.fp_1.id)])
        # Override to pull (FP-1 normally uses 'manufacture')
        item.write({"mrp_action": "pull"})
        wiz.make_procurement()
        # Verify picking was created (not MO)
        after_picking_count = self.stock_picking_obj.search_count(
            [
                ("move_ids.product_id", "=", self.fp_1.id),
                ("picking_type_id", "=", picking_type.id),
            ]
        )
        after_mo_count = self.mo_obj.search_count([("product_id", "=", self.fp_1.id)])
        self.assertGreater(
            after_picking_count,
            before_picking_count,
            "A stock picking should have been created for pull action",
        )
        self.assertEqual(
            after_mo_count,
            before_mo_count,
            "No new Manufacturing Order should have been created",
        )

        picking = self.stock_picking_obj.search(
            [
                ("move_ids.product_id", "=", self.fp_1.id),
                ("picking_type_id", "=", picking_type.id),
            ],
            order="id desc",
            limit=1,
        )
        self.assertTrue(picking, "Stock picking should exist")

        move = picking.move_ids.filtered(lambda m: m.product_id == self.fp_1)
        self.assertTrue(move, "Picking should have move for FP-1")
        self.assertEqual(
            move.product_uom_qty, item_qty, f"Move qty should be {item_qty}"
        )
        self.assertEqual(
            move.location_id,
            self.supplier_location,
            "Move should come from supplier location",
        )
        self.assertEqual(
            move.location_dest_id, item.location_id, "Move should go to item location"
        )

        self.assertEqual(
            planned_order.qty_released,
            qty_released_before + item_qty,
            "qty_released MUST increase - order must be marked as released",
        )

    def test_35_procure_wizard_mrp_action_override_to_pull_push(self):
        """Test override to 'pull_push' creates picking with correct data and
        updates planned_order."""
        mrp_inv = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.fp_1.id)], limit=1
        )
        self.assertTrue(mrp_inv, "No MRP inventory found for FP-1")

        planned_order = mrp_inv.planned_order_ids.filtered(
            lambda x: x.qty_released < x.mrp_qty
        )[:1]
        self.assertTrue(planned_order, "No planned order with pending qty")
        qty_released_before = planned_order.qty_released

        wiz = self.mrp_inventory_procure_wiz.with_context(
            active_model="mrp.inventory",
            active_ids=mrp_inv.ids,
            active_id=mrp_inv.id,
        ).create({})
        self.assertTrue(wiz.item_ids)
        item = wiz.item_ids[0]
        item_qty = item.qty

        # Create a pull_push rule for this location
        route = self.env["stock.route"].create(
            {
                "name": "Test route for pull_push (test_35)",
                "product_selectable": False,
                "warehouse_selectable": False,
                "company_id": self.company.id,
            }
        )
        picking_type = item.warehouse_id.int_type_id
        pull_push_rule = self.env["stock.rule"].create(
            {
                "name": "Test pull_push rule (test_35)",
                "route_id": route.id,
                "action": "pull_push",
                "location_src_id": self.supplier_location.id,
                "location_dest_id": item.location_id.id,
                "picking_type_id": picking_type.id,
                "company_id": self.company.id,
                "procure_method": "make_to_stock",
                "auto": "manual",
            }
        )
        self.assertTrue(pull_push_rule)
        self.assertEqual(pull_push_rule.action, "pull_push")
        # Count existing pickings and MOs for this product
        before_picking_count = self.stock_picking_obj.search_count(
            [
                ("move_ids.product_id", "=", self.fp_1.id),
                ("picking_type_id", "=", picking_type.id),
            ]
        )
        self.mo_obj.search([("product_id", "=", self.fp_1.id)]).unlink()
        before_mo_count = self.mo_obj.search_count([("product_id", "=", self.fp_1.id)])
        # Override to pull_push (FP-1 normally uses 'manufacture')
        item.write({"mrp_action": "pull_push"})
        wiz.make_procurement()
        # Verify picking was created (not MO)
        after_picking_count = self.stock_picking_obj.search_count(
            [
                ("move_ids.product_id", "=", self.fp_1.id),
                ("picking_type_id", "=", picking_type.id),
            ]
        )
        after_mo_count = self.mo_obj.search_count([("product_id", "=", self.fp_1.id)])
        self.assertGreater(
            after_picking_count,
            before_picking_count,
            "A stock picking should have been created for pull_push action",
        )
        self.assertEqual(
            after_mo_count,
            before_mo_count,
            "No new Manufacturing Order should have been created",
        )

        picking = self.stock_picking_obj.search(
            [
                ("move_ids.product_id", "=", self.fp_1.id),
                ("picking_type_id", "=", picking_type.id),
            ],
            order="id desc",
            limit=1,
        )
        self.assertTrue(picking, "Stock picking should exist")

        move = picking.move_ids.filtered(lambda m: m.product_id == self.fp_1)
        self.assertTrue(move, "Picking should have move for FP-1")
        self.assertEqual(
            move.product_uom_qty, item_qty, f"Move qty should be {item_qty}"
        )

        self.assertEqual(
            planned_order.qty_released,
            qty_released_before + item_qty,
            "qty_released MUST increase - order must be marked as released",
        )

    # NOTE: Test for 'push' action is not included because push rules work
    # differently in Odoo - they are triggered automatically when stock enters
    # a location, not through manual procurement calls. The _run_push method
    # expects self to be a singleton rule.

    def test_36_stock_rule_currency_domain_coverage(self):
        """Cover list->tuple domain conversion and values dict/list parsing."""
        rule = self.env["stock.rule"].search([], limit=1)
        self.assertTrue(rule, "Expected at least one stock.rule record")

        partner = self.env["res.partner"].create({"name": "Test Vendor"})
        currency_id = self.env.company.currency_id.id

        # 1) domain returned by super as list must be converted to tuple
        with patch.object(
            purchase_stock_rule.StockRule,
            "_make_po_get_domain",
            return_value=[("dummy", "=", 1)],
        ):
            domain = rule._make_po_get_domain(
                self.env.company, {"currency_id": currency_id}, partner
            )
        self.assertIsInstance(domain, tuple)
        self.assertIn(("currency_id", "=", currency_id), domain)

        # 2) values is dict -> currency_id picked from values.get("currency_id")
        with patch.object(
            purchase_stock_rule.StockRule,
            "_prepare_purchase_order",
            return_value={},
        ):
            res = rule._prepare_purchase_order(
                self.env.company,
                origins=["TEST"],
                values={"currency_id": currency_id},
            )
        self.assertEqual(res.get("currency_id"), currency_id)

        # 3) values is tuple/list -> currency_id picked from first dict having it
        values = (
            {"currency_id": False},
            {"currency_id": currency_id},
        )
        with patch.object(
            purchase_stock_rule.StockRule,
            "_prepare_purchase_order",
            return_value={},
        ):
            res = rule._prepare_purchase_order(self.env.company, ["TEST"], values)
        self.assertEqual(res.get("currency_id"), currency_id)

    def test_37_procure_wizard_onchange_and_make_procurement_validations(self):
        planned = self.planned_order_obj.search(
            [("product_id", "=", self.pp_1.id)], limit=1
        )
        self.assertTrue(planned)

        wiz = self.mrp_inventory_procure_wiz.with_context(
            active_model="mrp.planned.order",
            active_ids=planned.ids,
            active_id=planned.id,
        ).create({})
        self.assertTrue(wiz.item_ids)
        item = wiz.item_ids[0]

        # Cover branch: if not buy/product/warehouse -> supplier/currency reset
        item.mrp_action = "buy"
        item._onchange_purchase_defaults()
        self.assertTrue(item.supplier_id)
        self.assertTrue(item.currency_id)

        item.mrp_action = "manufacture"
        item._onchange_purchase_defaults()
        self.assertFalse(item.supplier_id)
        self.assertFalse(item.currency_id)

        # Cover validation: qty must be positive
        item.qty = 0.0
        with self.assertRaises(ValidationError) as exc:
            wiz.make_procurement()
        self.assertIn("Quantity must be positive", str(exc.exception))

    def test_38_grouped_procurement_multiple_actions(self):
        """Test grouped procurement with multiple items and different actions.
        Verifies that multiple planned orders create wizard with multiple items,
        executing correctly handles all items with their respective actions
        (buy, manufacture, pull) and updates all qty_released values.
        """
        # Arrange: Find multiple planned orders that will create wizard items
        # Criteria: not phantom, not fully released
        planned_orders = self.planned_order_obj.search(
            [
                ("mrp_action", "!=", "phantom"),
                ("qty_released", "<", 100000),
            ],
            limit=5,
        )
        self.assertGreaterEqual(
            len(planned_orders), 3, "Expected at least 3 valid planned orders"
        )

        # Ensure they have unreleased quantities
        for p in planned_orders[:3]:
            if p.qty_released >= p.mrp_qty:
                p.qty_released = 0.0

        planned_orders = planned_orders[:3]

        planned_1 = planned_orders[0]
        planned_2 = planned_orders[1]
        planned_3 = planned_orders[2]

        qty_released_1_before = planned_1.qty_released
        qty_released_2_before = planned_2.qty_released
        qty_released_3_before = planned_3.qty_released

        # Create wizard with multiple planned orders selected
        wiz = self.mrp_inventory_procure_wiz.with_context(
            active_model="mrp.planned.order",
            active_ids=planned_orders.ids,
            active_id=planned_1.id,
        ).create({})

        self.assertEqual(
            len(wiz.item_ids),
            3,
            "Expected wizard to have 3 items (one per planned order)",
        )

        # Force different actions on items to test grouped procurement
        item_1 = wiz.item_ids[0]
        item_2 = wiz.item_ids[1]
        item_3 = wiz.item_ids[2]

        # Force mrp_action to test different procurement paths
        # Only override if the product supports it (has BOM for manufacture, etc)
        if item_1.product_id.bom_ids:
            item_1.mrp_action = "manufacture"
        else:
            item_1.mrp_action = "buy"

        # Second item: always buy (safest option, works for all products)
        item_2.mrp_action = "buy"

        # Third item: try pull if possible, otherwise buy
        pull_rule = self.env["stock.rule"].search([("action", "=", "pull")], limit=1)
        if pull_rule:
            item_3.mrp_action = "pull"
        else:
            item_3.mrp_action = "buy"

        qty_1 = item_1.qty
        qty_2 = item_2.qty
        qty_3 = item_3.qty

        wiz.make_procurement()

        # Verify qty_released updated for ALL planned orders
        planned_1.invalidate_recordset()
        planned_2.invalidate_recordset()
        planned_3.invalidate_recordset()

        self.assertEqual(
            planned_1.qty_released,
            qty_released_1_before + qty_1,
            f"Expected planned_1.qty_released to be {qty_released_1_before + qty_1}, "
            f"got {planned_1.qty_released}",
        )
        self.assertEqual(
            planned_2.qty_released,
            qty_released_2_before + qty_2,
            f"Expected planned_2.qty_released to be {qty_released_2_before + qty_2}, "
            f"got {planned_2.qty_released}",
        )
        self.assertEqual(
            planned_3.qty_released,
            qty_released_3_before + qty_3,
            f"Expected planned_3.qty_released to be {qty_released_3_before + qty_3}, "
            f"got {planned_3.qty_released}",
        )
