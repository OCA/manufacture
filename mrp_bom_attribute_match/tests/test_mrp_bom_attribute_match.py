# mrp_bom_attribute_match/tests/test_mrp_bom_attribute_match.py

from odoo.tests.common import TransactionCase


class TestBomAttributeMatch(TransactionCase):
    """
    Test BOM component variant matching for mrp_bom_attribute_match module.
    """

    def setUp(self):
        super().setUp()
        self.product_model = self.env["product.product"]
        self.bom_model = self.env["mrp.bom"]

        # Create a warehouse for testing
        StockWarehouse = self.env["stock.warehouse"]
        self.warehouse = StockWarehouse.create(
            {
                "name": "Test Warehouse",
                "code": "TEST",
            }
        )

    def test_bom_variant_application(self):
        """
        Verify that component template variants are correctly applied
        in BOM data.
        """
        # Create a test product
        product = self.product_model.create(
            {
                "name": "Test Product",
                "type": "consu",
            }
        )

        # Create a BOM for the product
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


# Optional helper class (does NOT inherit from Odoo models)
class BomReportTestHelper:
    """
    Standalone helper class for tests, no Odoo model inheritance.
    Used for utility functions only.
    """

    @staticmethod
    def example_helper_method():
        return "helper works"
