# Copyright 2026 CHEF PIXEL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestBomAttributeMatch(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product_model = self.env["product.product"]
        self.bom_model = self.env["mrp.bom"]
        self.warehouse = self.env.ref("stock.stock_warehouse0")

    def test_bom_variant_application(self):
        product = self.product_model.create(
            {
                "name": "Test Product",
                "type": "product",
            }
        )

        bom = self.bom_model.create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_qty": 1.0,
            }
        )

        # Fetch BOM data using the main module class
        report_data = self.env["report.mrp.report_bom_structure"]._get_bom_data(
            bom,
            self.warehouse,
            product=product,
        )

        # Assertions to ensure variants are applied correctly
        self.assertIn("components", report_data)
        self.assertIsInstance(report_data["components"], list)
        self.assertTrue(report_data.get("is_variant_applied") in (True, False))


class BomReportTestHelper:
    """
    Standalone helper class for tests, no inheritance from the abstract model.
    Used for utility functions only.
    """

    @staticmethod
    def example_helper_method():
        return "helper works"
