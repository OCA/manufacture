# Copyright 2025 Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestMrpBomBatchLimit(TransactionCase):
    def setUp(self):
        super().setUp()

        # Create a product
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
            }
        )

        # Create a BoM with batch limits
        self.bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product.product_tmpl_id,
                "product_qty": 1.0,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "enable_batch_limit": True,
                "min_batch_qty": 5.0,
                "max_batch_qty": 20.0,
            }
        )

    def test_bom_batch_limit_validation(self):
        """Test BoM batch limit validation"""
        # Test valid limits
        self.bom.min_batch_qty = 10.0
        self.bom.max_batch_qty = 50.0
        self.bom._check_batch_limits()

        # Test invalid limits (min > max)
        with self.assertRaises(ValidationError) as cm:
            self.bom.min_batch_qty = 30.0
            self.bom.max_batch_qty = 20.0
            self.bom._check_batch_limits()
        self.assertIn("minimum batch quantity cannot be greater", str(cm.exception))

        # Test negative limits
        with self.assertRaises(ValidationError) as cm:
            self.bom.min_batch_qty = -5.0
            self.bom._check_batch_limits()
        self.assertIn("must be positive", str(cm.exception))

    def test_production_warning_below_min(self):
        """Test warning when quantity is below minimum"""
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 3.0,  # Below min (5.0)
                "bom_id": self.bom.id,
            }
        )

        self.assertTrue(mo.batch_limit_warning)
        self.assertIn("below minimum", mo.batch_limit_message)
        self.assertIn("3.00", mo.batch_limit_message)
        self.assertIn("5.00", mo.batch_limit_message)

    def test_production_warning_above_max(self):
        """Test warning when quantity exceeds maximum"""
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 25.0,  # Above max (20.0)
                "bom_id": self.bom.id,
            }
        )

        self.assertTrue(mo.batch_limit_warning)
        self.assertIn("exceeds maximum", mo.batch_limit_message)
        self.assertIn("25.00", mo.batch_limit_message)
        self.assertIn("20.00", mo.batch_limit_message)

    def test_production_no_warning_within_limits(self):
        """Test no warning when quantity is within limits"""
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 10.0,  # Within limits (5.0 - 20.0)
                "bom_id": self.bom.id,
            }
        )

        self.assertFalse(mo.batch_limit_warning)
        self.assertFalse(mo.batch_limit_message)

    def test_production_confirm_blocked(self):
        """Test that confirmation is blocked when limits are violated"""
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 3.0,  # Below min
                "bom_id": self.bom.id,
            }
        )

        with self.assertRaises(UserError) as cm:
            mo.action_confirm()
        self.assertIn("below minimum", str(cm.exception))

    def test_production_confirm_allowed(self):
        """Test that confirmation is allowed when limits are respected"""
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 10.0,  # Within limits
                "bom_id": self.bom.id,
            }
        )

        # Should not raise an error
        mo.action_confirm()
        self.assertEqual(mo.state, "confirmed")

    def test_no_batch_limit_no_warning(self):
        """Test no warning when batch limit is disabled"""
        self.bom.enable_batch_limit = False

        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 100.0,  # Any quantity
                "bom_id": self.bom.id,
            }
        )

        self.assertFalse(mo.batch_limit_warning)
        self.assertFalse(mo.batch_limit_message)
