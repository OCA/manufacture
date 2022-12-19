# Copyright 2018-22 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta

from odoo.addons.mrp_multi_level.tests.common import TestMrpMultiLevelCommon


class TestMrpMultiLevelEstimate(TestMrpMultiLevelCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.estimate_obj = cls.env["stock.demand.estimate"]

        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

        # Create new clean area:
        cls.estimate_loc = cls.loc_obj.create(
            {
                "name": "Test location for estimates",
                "usage": "internal",
                "location_id": cls.wh.view_location_id.id,
            }
        )
        cls.estimate_area = cls.mrp_area_obj.create(
            {
                "name": "Test",
                "warehouse_id": cls.wh.id,
                "location_id": cls.estimate_loc.id,
            }
        )
        cls.test_mrp_parameter = cls.product_mrp_area_obj.create(
            {
                "product_id": cls.prod_test.id,
                "mrp_area_id": cls.estimate_area.id,
                "mrp_nbr_days": 7,
            }
        )

        # Create 3 consecutive estimates of 1 week length each.
        today = datetime.today().replace(hour=0)
        date_start_1 = today - timedelta(days=3)
        date_end_1 = date_start_1 + timedelta(days=6)
        date_start_2 = date_end_1 + timedelta(days=1)
        date_end_2 = date_start_2 + timedelta(days=6)
        date_start_3 = date_end_2 + timedelta(days=1)
        date_end_3 = date_start_3 + timedelta(days=6)
        start_dates = [date_start_1, date_start_2, date_start_3]
        end_dates = [date_end_1, date_end_2, date_end_3]

        cls.date_within_ranges = today - timedelta(days=2)
        cls.date_without_ranges = today + timedelta(days=150)

        qty = 140.0
        for sd, ed in zip(start_dates, end_dates):
            qty += 70.0
            cls._create_demand_estimate(cls.prod_test, cls.stock_location, sd, ed, qty)
            cls._create_demand_estimate(cls.prod_test, cls.estimate_loc, sd, ed, qty)

        cls.mrp_multi_level_wiz.create({}).run_mrp_multi_level()

    @classmethod
    def _create_demand_estimate(cls, product, location, date_from, date_to, qty):
        cls.estimate_obj.create(
            {
                "product_id": product.id,
                "location_id": location.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": qty,
                "manual_date_from": date_from,
                "manual_date_to": date_to,
            }
        )

    def test_01_demand_estimates(self):
        """Tests demand estimates integration."""
        estimates = self.estimate_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("location_id", "=", self.stock_location.id),
            ]
        )
        self.assertEqual(len(estimates), 3)
        moves = self.mrp_move_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("mrp_area_id", "=", self.mrp_area.id),
            ]
        )
        # 3 weeks - 3 days in the past = 18 days of valid estimates:
        moves_from_estimates = moves.filtered(lambda m: m.mrp_type == "d")
        self.assertEqual(len(moves_from_estimates), 18)
        quantities = moves_from_estimates.mapped("mrp_qty")
        self.assertIn(-30.0, quantities)  # 210 a week => 30.0 dayly:
        self.assertIn(-40.0, quantities)  # 280 a week => 40.0 dayly:
        self.assertIn(-50.0, quantities)  # 350 a week => 50.0 dayly:
        plans = self.planned_order_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("mrp_area_id", "=", self.mrp_area.id),
            ]
        )
        action = list(set(plans.mapped("mrp_action")))
        self.assertEqual(len(action), 1)
        self.assertEqual(action[0], "buy")
        self.assertEqual(len(plans), 18)
        inventories = self.mrp_inventory_obj.search(
            [("mrp_area_id", "=", self.estimate_area.id)]
        )
        self.assertEqual(len(inventories), 18)

    def test_02_demand_estimates_group_plans(self):
        """Test requirement grouping functionality, `nbr_days`."""
        estimates = self.estimate_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("location_id", "=", self.estimate_loc.id),
            ]
        )
        self.assertEqual(len(estimates), 3)
        moves = self.mrp_move_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("mrp_area_id", "=", self.estimate_area.id),
            ]
        )
        supply_plans = self.planned_order_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("mrp_area_id", "=", self.estimate_area.id),
            ]
        )
        # 3 weeks - 3 days in the past = 18 days of valid estimates:
        moves_from_estimates = moves.filtered(lambda m: m.mrp_type == "d")
        self.assertEqual(len(moves_from_estimates), 18)
        # 18 days of demand / 7 nbr_days = 2.57 => 3 supply moves expected.
        self.assertEqual(len(supply_plans), 3)
        quantities = supply_plans.mapped("mrp_qty")
        week_1_expected = sum(moves_from_estimates[0:7].mapped("mrp_qty"))
        self.assertIn(abs(week_1_expected), quantities)
        week_2_expected = sum(moves_from_estimates[7:14].mapped("mrp_qty"))
        self.assertIn(abs(week_2_expected), quantities)
        week_3_expected = sum(moves_from_estimates[14:].mapped("mrp_qty"))
        self.assertIn(abs(week_3_expected), quantities)

    def test_03_group_demand_estimates(self):
        """Test demand grouping functionality, `group_estimate_days`."""
        self.test_mrp_parameter.group_estimate_days = 7
        self.mrp_multi_level_wiz.create(
            {"mrp_area_ids": [(6, 0, self.estimate_area.ids)]}
        ).run_mrp_multi_level()
        estimates = self.estimate_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("location_id", "=", self.estimate_loc.id),
            ]
        )
        self.assertEqual(len(estimates), 3)
        moves = self.mrp_move_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("mrp_area_id", "=", self.estimate_area.id),
            ]
        )
        # 3 weekly estimates, demand from estimates grouped in batches of 7
        # days = 3 days of estimates mrp moves:
        moves_from_estimates = moves.filtered(lambda m: m.mrp_type == "d")
        self.assertEqual(len(moves_from_estimates), 3)
        # 210 weekly -> 30 daily -> 30 * 4 days not consumed = 120
        self.assertEqual(moves_from_estimates[0].mrp_qty, -120)
        self.assertEqual(moves_from_estimates[1].mrp_qty, -280)
        self.assertEqual(moves_from_estimates[2].mrp_qty, -350)
        # Test group_estimate_days greater than date range, it should not
        # generate greater demand.
        self.test_mrp_parameter.group_estimate_days = 10
        self.mrp_multi_level_wiz.create(
            {"mrp_area_ids": [(6, 0, self.estimate_area.ids)]}
        ).run_mrp_multi_level()
        moves = self.mrp_move_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("mrp_area_id", "=", self.estimate_area.id),
            ]
        )
        moves_from_estimates = moves.filtered(lambda m: m.mrp_type == "d")
        self.assertEqual(len(moves_from_estimates), 3)
        self.assertEqual(moves_from_estimates[0].mrp_qty, -120)
        self.assertEqual(moves_from_estimates[1].mrp_qty, -280)
        self.assertEqual(moves_from_estimates[2].mrp_qty, -350)
        # Test group_estimate_days smaller than date range, it should not
        # generate greater demand.
        self.test_mrp_parameter.group_estimate_days = 5
        self.mrp_multi_level_wiz.create(
            {"mrp_area_ids": [(6, 0, self.estimate_area.ids)]}
        ).run_mrp_multi_level()
        moves = self.mrp_move_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("mrp_area_id", "=", self.estimate_area.id),
            ]
        )
        moves_from_estimates = moves.filtered(lambda m: m.mrp_type == "d")
        self.assertEqual(len(moves_from_estimates), 5)
        # Week 1 partially consumed, so only 4 remaining days considered.
        # 30 daily x 4 days = 120
        self.assertEqual(moves_from_estimates[0].mrp_qty, -120)
        # Week 2 divided in 2 (40 daily) -> 5 days = 200, 2 days = 80
        self.assertEqual(moves_from_estimates[1].mrp_qty, -200)
        self.assertEqual(moves_from_estimates[2].mrp_qty, -80)
        # Week 3 divided in 2, (50 daily) -> 5 days = 250, 2 days = 100
        self.assertEqual(moves_from_estimates[3].mrp_qty, -250)
        self.assertEqual(moves_from_estimates[4].mrp_qty, -100)

    def test_04_group_demand_estimates_rounding(self):
        """Test demand grouping functionality, `group_estimate_days` and rounding."""
        self.test_mrp_parameter.group_estimate_days = 7
        self.uom_unit.rounding = 1.00

        estimates = self.estimate_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("location_id", "=", self.estimate_loc.id),
            ]
        )
        self.assertEqual(len(estimates), 3)
        # Change qty of estimates to quantities that divided by 7 days return a decimal result
        qty = 400
        for estimate in estimates:
            estimate.product_uom_qty = qty
            qty += 100

        self.mrp_multi_level_wiz.create(
            {"mrp_area_ids": [(6, 0, self.estimate_area.ids)]}
        ).run_mrp_multi_level()
        moves = self.mrp_move_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("mrp_area_id", "=", self.estimate_area.id),
            ]
        )
        # 3 weekly estimates, demand from estimates grouped in batches of 7
        # days = 3 days of estimates mrp moves:
        moves_from_estimates = moves.filtered(lambda m: m.mrp_type == "d")
        self.assertEqual(len(moves_from_estimates), 3)
        # Rounding should be done at the end of the calculation, using the daily
        # quantity already rounded can lead to errors.
        # 400 weekly -> 57.41 daily -> 57.41 * 4 days not consumed = 228,57 = 229
        self.assertEqual(moves_from_estimates[0].mrp_qty, -229)
        # 500 weekly -> 71.42 daily -> 71,42 * 7 = 500
        self.assertEqual(moves_from_estimates[1].mrp_qty, -500)
        # 600 weekly -> 85.71 daily -> 85.71 * 7 = 600
        self.assertEqual(moves_from_estimates[2].mrp_qty, -600)

    def test_05_estimate_and_other_sources_strat(self):
        """Tests demand estimates and other sources strategies."""
        estimates = self.estimate_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("location_id", "=", self.estimate_loc.id),
            ]
        )
        self.assertEqual(len(estimates), 3)
        self._create_picking_out(
            self.prod_test, 25, self.date_within_ranges, location=self.estimate_loc
        )
        self._create_picking_out(
            self.prod_test, 25, self.date_without_ranges, location=self.estimate_loc
        )
        # 1. "all"
        self.estimate_area.estimate_demand_and_other_sources_strat = "all"
        self.mrp_multi_level_wiz.create(
            {"mrp_area_ids": [(6, 0, self.estimate_area.ids)]}
        ).run_mrp_multi_level()
        moves = self.mrp_move_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("mrp_area_id", "=", self.estimate_area.id),
            ]
        )
        # 3 weeks - 3 days in the past = 18 days of valid estimates:
        demand_from_estimates = moves.filtered(
            lambda m: m.mrp_type == "d" and m.mrp_origin == "fc"
        )
        demand_from_other_sources = moves.filtered(
            lambda m: m.mrp_type == "d" and m.mrp_origin != "fc"
        )
        self.assertEqual(len(demand_from_estimates), 18)
        self.assertEqual(len(demand_from_other_sources), 2)

        # 2. "ignore_others_if_estimates"
        self.estimate_area.estimate_demand_and_other_sources_strat = (
            "ignore_others_if_estimates"
        )
        self.mrp_multi_level_wiz.create(
            {"mrp_area_ids": [(6, 0, self.estimate_area.ids)]}
        ).run_mrp_multi_level()
        moves = self.mrp_move_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("mrp_area_id", "=", self.estimate_area.id),
            ]
        )
        demand_from_estimates = moves.filtered(
            lambda m: m.mrp_type == "d" and m.mrp_origin == "fc"
        )
        demand_from_other_sources = moves.filtered(
            lambda m: m.mrp_type == "d" and m.mrp_origin != "fc"
        )
        self.assertEqual(len(demand_from_estimates), 18)
        self.assertEqual(len(demand_from_other_sources), 0)

        # 3. "ignore_overlapping"
        self.estimate_area.estimate_demand_and_other_sources_strat = (
            "ignore_overlapping"
        )
        self.mrp_multi_level_wiz.create(
            {"mrp_area_ids": [(6, 0, self.estimate_area.ids)]}
        ).run_mrp_multi_level()
        moves = self.mrp_move_obj.search(
            [
                ("product_id", "=", self.prod_test.id),
                ("mrp_area_id", "=", self.estimate_area.id),
            ]
        )
        demand_from_estimates = moves.filtered(
            lambda m: m.mrp_type == "d" and m.mrp_origin == "fc"
        )
        demand_from_other_sources = moves.filtered(
            lambda m: m.mrp_type == "d" and m.mrp_origin != "fc"
        )
        self.assertEqual(len(demand_from_estimates), 18)
        self.assertEqual(len(demand_from_other_sources), 1)
        self.assertEqual(
            demand_from_other_sources.mrp_date, self.date_without_ranges.date()
        )
