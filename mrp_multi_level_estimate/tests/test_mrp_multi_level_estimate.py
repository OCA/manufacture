# Copyright 2018-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta

from dateutil.rrule import WEEKLY

from odoo.addons.mrp_multi_level.tests.common import TestMrpMultiLevelCommon


class TestMrpMultiLevelEstimate(TestMrpMultiLevelCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.estimate_obj = cls.env["stock.demand.estimate"]

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
        cls.product_mrp_area_obj.create(
            {
                "product_id": cls.prod_test.id,
                "mrp_area_id": cls.estimate_area.id,
                "mrp_nbr_days": 7,
            }
        )

        # Create Date Ranges:
        cls.dr_type = cls.env["date.range.type"].create(
            {"name": "Weeks", "company_id": False, "allow_overlap": False}
        )
        today = datetime.today().replace(hour=0)
        generator = cls.env["date.range.generator"].create(
            {
                "date_start": today - timedelta(days=3),
                "name_prefix": "W-",
                "type_id": cls.dr_type.id,
                "duration_count": 1,
                "unit_of_time": str(WEEKLY),
                "count": 3,
            }
        )
        generator.action_apply()

        # Create Demand Estimates:
        ranges = cls.env["date.range"].search([("type_id", "=", cls.dr_type.id)])
        qty = 140.0
        for dr in ranges:
            qty += 70.0
            cls._create_demand_estimate(cls.prod_test, cls.stock_location, dr, qty)
            cls._create_demand_estimate(cls.prod_test, cls.estimate_loc, dr, qty)

        cls.mrp_multi_level_wiz.create({}).run_mrp_multi_level()

    @classmethod
    def _create_demand_estimate(cls, product, location, date_range, qty):
        cls.estimate_obj.create(
            {
                "product_id": product.id,
                "location_id": location.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": qty,
                "date_range_id": date_range.id,
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

    def test_02_group_demand_estimates(self):
        """Test demand grouping functionality, `nbr_days`."""
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
