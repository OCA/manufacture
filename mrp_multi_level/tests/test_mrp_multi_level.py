# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import date, datetime, timedelta

from odoo import fields

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
        mo_date_start = fields.Date.to_date(mos.date_start)
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

    def test_10_special_scenario_1(self):
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

    def test_11_bom_line_attribute_value_skip(self):
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

    def test_12_timezone_handling(self):
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

    def test_13_timezone_not_set(self):
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

    def test_14_units_case(self):
        """When a product has a different purchase unit of measure than
        the general unit of measure and the supply is coming from an RFQ"""
        prod_uom_test_inventory_lines = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.prod_uom_test.id)]
        )
        self.assertEqual(len(prod_uom_test_inventory_lines), 1)
        self.assertEqual(prod_uom_test_inventory_lines.supply_qty, 12.0)
        # Supply qty has to be 12 has a dozen of units are in a RFQ.

    def test_15_phantom_comp_planning(self):
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

    def test_16_supply_method(self):
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
        # because of the issue discussed here https://github.com/odoo/odoo/pull/188846
        # we need to apply routes explicitly in the proper order (by sequence)
        self.fp_4.route_ids = [
            (
                6,
                0,
                (
                    self.env.ref("stock.route_warehouse0_mto")
                    + self.env.ref("purchase_stock.route_warehouse0_buy")
                    + self.env.ref("mrp.route_warehouse0_manufacture")
                ).ids,
            )
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

    def test_17_priorize_safety_stock(self):
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
        for test_vals, inv in zip(expected, inventory, strict=True):
            for key in test_vals:
                self.assertEqual(
                    test_vals[key],
                    inv[key],
                    f"unexpected value for {key}: {inv[key]} "
                    f"(expected {test_vals[key]} on {inv.date})",
                )

    def test_18_on_hand_with_lots(self):
        """Check that on-hand is correctly computed when tracking by lots."""
        lots_line_1 = self.mrp_inventory_obj.search(
            [("product_mrp_area_id.product_id", "=", self.product_lots.id)]
        )
        self.assertEqual(len(lots_line_1), 1)
        self.assertEqual(lots_line_1.initial_on_hand_qty, 210)
        self.assertEqual(lots_line_1.final_on_hand_qty, 185)

    def test_19_prioritize_safety_stock_grouped_1(self):
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
        for test_vals, inv in zip(expected, inventory, strict=True):
            for key in test_vals:
                self.assertEqual(
                    test_vals[key],
                    inv[key],
                    f"unexpected value for {key}: {inv[key]} "
                    f"(expected {test_vals[key]} on {inv.date})",
                )

    def test_20_prioritize_safety_stock_grouped_2(self):
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
        for test_vals, inv in zip(expected, inventory, strict=True):
            for key in test_vals:
                self.assertEqual(
                    test_vals[key],
                    inv[key],
                    f"unexpected value for {key}: {inv[key]} "
                    f"(expected {test_vals[key]} on {inv.date})",
                )

    def test_21_prioritize_safety_stock_grouped_3(self):
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
        for test_vals, inv in zip(expected, inventory, strict=True):
            for key in test_vals:
                self.assertEqual(
                    test_vals[key],
                    inv[key],
                    f"unexpected value for {key}: {inv[key]} "
                    f"(expected {test_vals[key]} on {inv.date})",
                )

    def test_22_prioritize_safety_stock_with_mrp_moves_today(self):
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
        for test_vals, inv in zip(expected, inventory, strict=True):
            for key in test_vals:
                self.assertEqual(
                    test_vals[key],
                    inv[key],
                    f"unexpected value for {key}: {inv[key]} "
                    f"(expected {test_vals[key]} on {inv.date})",
                )

    def test_23_prioritize_safety_stock_with_mrp_moves_today_grouped(self):
        """Test grouped demand MRP but with moves today. Safety stock should not be
        ordered.
        """
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
        for test_vals, inv in zip(expected, inventory, strict=True):
            for key in test_vals:
                self.assertEqual(
                    test_vals[key],
                    inv[key],
                    f"unexpected value for {key}: {inv[key]} "
                    f"(expected {test_vals[key]} on {inv.date})",
                )

    def test_24_phantom_comp_on_hand(self):
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
