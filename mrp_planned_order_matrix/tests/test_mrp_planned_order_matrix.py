# Copyright 2020-21 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.rrule import MONTHLY

from odoo import fields

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
            {"name": "Test Product 1", "type": "product", "default_code": "PROD1"}
        )
        # Create a product mrp area:
        cls.product_mrp_area_1 = cls.product_mrp_area_obj.create(
            {"product_id": cls.product_1.id, "mrp_area_id": cls.mrp_area.id}
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
        wiz.create_sheet()
        sheets = self.env["mrp.planned.order.sheet"].search([])
        for sheet in sheets:
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
            mrp_planned_order_sheet_lines = self.env[
                "mrp.planned.order.sheet.line"
            ].search([("date_range_id", "in", ranges.ids)])
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
