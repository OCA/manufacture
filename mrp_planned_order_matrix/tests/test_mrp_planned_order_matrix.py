# Copyright 2020-21 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.rrule import MONTHLY

from odoo import fields
from odoo.exceptions import UserError, ValidationError

from odoo.addons.mrp_multi_level.tests.common import TestMrpMultiLevelCommon


class TestMrpPlannedOrderMatrix(TestMrpMultiLevelCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mrp_planned_order_matrix_wiz = cls.env["mrp.planned.order.wizard"]
        cls.drt_monthly = cls.env["date.range.type"].create(
            {"name": "Month", "allow_overlap": False}
        )

        generator = cls.env["date.range.generator"]
        generator = generator.create(
            {
                "date_start": "1943-01-01",
                "name_prefix": "1943-",
                "type_id": cls.drt_monthly.id,
                "duration_count": 1,
                "unit_of_time": str(MONTHLY),
                "count": 12,
            }
        )
        generator.action_apply()

        # Create a product:
        cls.product_1 = cls.product_obj.create(
            {
                "name": "Test Product 1",
                "type": "consu",
                "is_storable": True,
                "default_code": "PROD1",
            }
        )
        # Create a product mrp area:
        cls.product_mrp_area_1 = cls.product_mrp_area_obj.create(
            {
                "product_id": cls.product_1.id,
                "mrp_area_id": cls.mrp_area.id,
            }
        )

    def test_01_mrp_planned_order_matrix(self):
        """Tests creation of planned orders using matrix wizard."""
        wiz = self.mrp_planned_order_matrix_wiz
        wiz = wiz.create(
            {
                "date_start": "1943-01-01",
                "date_end": "1943-12-31",
                "date_range_type_id": self.drt_monthly.id,
                "product_mrp_area_ids": [(6, 0, [self.product_mrp_area_1.id])],
            }
        )
        res = wiz.create_sheet()
        sheet = self.env["mrp.planned.order.sheet"].browse(res["res_id"])
        self.assertEqual(
            len(sheet.line_ids),
            12,
            "There should be 12 lines.",
        )
        self.assertEqual(
            fields.Date.to_string(sheet.date_start),
            "1943-01-01",
            "The date start should be 1943-01-01",
        )
        self.assertEqual(
            fields.Date.to_string(sheet.date_end),
            "1943-12-31",
            "The date end should be 1943-12-31",
        )
        for line in sheet.line_ids:
            line.product_qty = 1
            self.assertEqual(
                line.product_mrp_area_id.product_id.id,
                self.product_1.id,
                "The product does not match in the line",
            )
        sheet.button_validate()
        ranges = self.env["date.range"].search(
            [("type_id", "=", self.drt_monthly.id)],
        )
        mrp_planned_order_sheet_lines = self.env["mrp.planned.order.sheet.line"].search(
            [("date_range_id", "in", ranges.ids)]
        )
        self.assertEqual(
            len(mrp_planned_order_sheet_lines),
            12,
            "There should be 12 estimate records.",
        )
        for planned_order in mrp_planned_order_sheet_lines:
            self.assertEqual(
                planned_order.product_mrp_area_id.product_id.id,
                self.product_1.id,
                "The product does not match in the estimate",
            )
            self.assertEqual(
                planned_order.product_qty,
                1,
                "The product qty does not match",
            )
        mrp_planned_orders = self.env["mrp.planned.order"].search(
            [("product_mrp_area_id", "=", self.product_mrp_area_1.id)]
        )
        self.assertEqual(
            len(mrp_planned_orders),
            12,
            "There should be 12 planned order records.",
        )

    def test_02_dates_validation(self):
        with self.assertRaises(ValidationError):
            self.mrp_planned_order_matrix_wiz.create(
                {
                    "date_start": "1943-12-31",
                    "date_end": "1943-01-01",
                    "date_range_type_id": self.drt_monthly.id,
                    "product_mrp_area_ids": [(6, 0, [self.product_mrp_area_1.id])],
                }
            )

    def test_03_create_sheet_no_mrp_area(self):
        wiz = self.mrp_planned_order_matrix_wiz.create(
            {
                "date_start": "1943-01-01",
                "date_end": "1943-12-31",
                "date_range_type_id": self.drt_monthly.id,
                "product_mrp_area_ids": [(6, 0, [])],
            }
        )
        with self.assertRaises(ValidationError):
            wiz.create_sheet()

    def test_04_onchange_dates_no_ranges(self):
        wiz = self.mrp_planned_order_matrix_wiz.create(
            {
                "date_start": "2000-01-01",
                "date_end": "2000-12-31",
                "date_range_type_id": self.drt_monthly.id,
                "product_mrp_area_ids": [(6, 0, [self.product_mrp_area_1.id])],
            }
        )
        with self.assertRaises(UserError):
            wiz.create_sheet()

    def test_05_onchange_dates_with_items_and_button_validate(self):
        order_1 = self.env["mrp.planned.order"].create(
            {
                "product_mrp_area_id": self.product_mrp_area_1.id,
                "mrp_qty": 5.0,
                "due_date": "1943-01-15",
                "order_release_date": "1943-01-15",
                "fixed": True,
            }
        )
        order_2 = self.env["mrp.planned.order"].create(
            {
                "product_mrp_area_id": self.product_mrp_area_1.id,
                "mrp_qty": 10.0,
                "due_date": "1943-02-15",
                "order_release_date": "1943-02-15",
                "fixed": True,
            }
        )
        order_3 = self.env["mrp.planned.order"].create(
            {
                "product_mrp_area_id": self.product_mrp_area_1.id,
                "mrp_qty": 20.0,
                "due_date": "1943-03-15",
                "order_release_date": "1943-03-15",
                "fixed": True,
            }
        )

        wiz = self.mrp_planned_order_matrix_wiz.create(
            {
                "date_start": "1943-01-01",
                "date_end": "1943-12-31",
                "date_range_type_id": self.drt_monthly.id,
                "product_mrp_area_ids": [(6, 0, [self.product_mrp_area_1.id])],
            }
        )
        res = wiz.create_sheet()
        sheet = self.env["mrp.planned.order.sheet"].browse(res["res_id"])

        line_jan = sheet.line_ids.filtered(
            lambda rec: rec.date_range_id.date_start
            == fields.Date.from_string("1943-01-01")
        )
        self.assertEqual(line_jan.product_qty, 5.0)
        self.assertIn(order_1.id, line_jan.mrp_planned_order_ids.ids)

        line_feb = sheet.line_ids.filtered(
            lambda rec: rec.date_range_id.date_start
            == fields.Date.from_string("1943-02-01")
        )
        self.assertEqual(line_feb.product_qty, 10.0)
        self.assertIn(order_2.id, line_feb.mrp_planned_order_ids.ids)

        # To cover early return in _onchange_dates
        sheet.date_start = False
        sheet._onchange_dates()
        sheet.date_start = fields.Date.from_string("1943-01-01")

        # Modify quantities
        line_jan.product_qty = 5.0
        line_feb.product_qty = 15.0
        line_mar = sheet.line_ids.filtered(
            lambda rec: rec.date_range_id.date_start
            == fields.Date.from_string("1943-03-01")
        )
        line_mar.product_qty = 0.0

        sheet.button_validate()

        self.assertEqual(order_1.mrp_qty, 5.0)
        self.assertTrue(order_1.exists())
        self.assertEqual(order_2.mrp_qty, 15.0)
        self.assertFalse(order_3.exists())

    def test_06_calendar_lead_time(self):
        calendar = self.env["resource.calendar"].create(
            {"name": "Test Calendar", "company_id": self.env.company.id}
        )
        self.mrp_area.calendar_id = calendar.id
        self.product_mrp_area_1.mrp_lead_time = 5

        wiz = self.mrp_planned_order_matrix_wiz.create(
            {
                "date_start": "1943-04-01",
                "date_end": "1943-04-30",
                "date_range_type_id": self.drt_monthly.id,
                "product_mrp_area_ids": [(6, 0, [self.product_mrp_area_1.id])],
            }
        )
        res = wiz.create_sheet()
        sheet = self.env["mrp.planned.order.sheet"].browse(res["res_id"])
        line_apr = sheet.line_ids.filtered(
            lambda rec: rec.date_range_id.date_start
            == fields.Date.from_string("1943-04-01")
        )
        line_apr.product_qty = 10.0
        sheet.button_validate()

        order = self.env["mrp.planned.order"].search(
            [
                ("product_mrp_area_id", "=", self.product_mrp_area_1.id),
                ("mrp_qty", "=", 10.0),
            ],
            limit=1,
        )
        self.assertTrue(order)

    def test_07_no_calendar_lead_time(self):
        self.mrp_area.calendar_id = False
        self.product_mrp_area_1.mrp_lead_time = 5

        wiz = self.mrp_planned_order_matrix_wiz.create(
            {
                "date_start": "1943-05-01",
                "date_end": "1943-05-31",
                "date_range_type_id": self.drt_monthly.id,
                "product_mrp_area_ids": [(6, 0, [self.product_mrp_area_1.id])],
            }
        )
        res = wiz.create_sheet()
        sheet = self.env["mrp.planned.order.sheet"].browse(res["res_id"])
        line_may = sheet.line_ids.filtered(
            lambda rec: rec.date_range_id.date_start
            == fields.Date.from_string("1943-05-01")
        )
        line_may.product_qty = 10.0
        sheet.button_validate()

        order = self.env["mrp.planned.order"].search(
            [
                ("product_mrp_area_id", "=", self.product_mrp_area_1.id),
                ("mrp_qty", "=", 10.0),
                ("due_date", "=", "1943-05-01"),
            ],
            limit=1,
        )
        self.assertTrue(order)
        self.assertEqual(
            fields.Date.to_string(order.order_release_date),
            "1943-04-26",
        )
