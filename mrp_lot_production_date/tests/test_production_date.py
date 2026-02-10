# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime, timedelta

from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestMrpLotProductionDate(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create a product for BOM
        cls.bom_product = cls.env["product.product"].create(
            {
                "name": "Test BOM Product",
                "tracking": "lot",
            }
        )

        # Create a component for BOM
        cls.component = cls.env["product.product"].create(
            {
                "name": "Test Component",
                "tracking": "lot",
            }
        )

        # Create BOM
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.bom_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "product_uom_id": cls.env.ref("uom.product_uom_unit").id,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.component.id,
                            "product_qty": 1.0,
                            "product_uom_id": cls.env.ref("uom.product_uom_unit").id,
                        },
                    )
                ],
            }
        )

        # Create a product with expiration tracking
        cls.product_expiring = cls.env["product.product"].create(
            {
                "name": "Test Product with Expiration",
                "use_expiration_date": True,
                "tracking": "lot",
            }
        )

        # Set expiration times on the product template
        cls.product_expiring.product_tmpl_id.write(
            {
                "expiration_time": 30,
                "use_time": 7,
                "removal_time": 3,
                "alert_time": 10,
            }
        )

        # Create a product without expiration tracking
        cls.product_non_expiring = cls.env["product.product"].create(
            {
                "name": "Test Product without Expiration",
                "use_expiration_date": False,
                "tracking": "lot",
            }
        )

    @classmethod
    def _create_manufacturing_order(cls, bom, product_qty=1):
        with Form(cls.env["mrp.production"]) as form:
            form.bom_id = bom
            form.product_qty = product_qty
            order = form.save()
            order.invalidate_recordset()
            return order

    @classmethod
    def _validate_manufacturing_order(cls, order):
        order.action_confirm()
        order.action_assign()
        # To ease the test we generate the lot manually, but this could be
        # handled automatically by calling the 'Immediate production' wizard
        order.action_generate_serial()
        order.button_mark_done()

    def test_lot_production_date(self):
        order = self._create_manufacturing_order(self.bom)
        self._validate_manufacturing_order(order)
        self.assertTrue(order.lot_producing_id.production_date)

    def test_production_date_sets_expiration_dates(self):
        """Test that setting production date automatically sets expiration dates."""
        production_date = datetime(2024, 1, 1, 10, 0, 0)

        # Create lot with production date
        lot = self.env["stock.lot"].create(
            {
                "name": "TEST-LOT-001",
                "product_id": self.product_expiring.id,
                "production_date": production_date,
            }
        )

        # Check that expiration dates are set correctly
        expected_expiration = production_date + timedelta(days=30)
        expected_use_date = expected_expiration - timedelta(days=7)
        expected_removal_date = expected_expiration - timedelta(days=3)
        expected_alert_date = expected_expiration - timedelta(days=10)

        self.assertEqual(lot.expiration_date, expected_expiration)
        self.assertEqual(lot.use_date, expected_use_date)
        self.assertEqual(lot.removal_date, expected_removal_date)
        self.assertEqual(lot.alert_date, expected_alert_date)

    def test_production_date_change_updates_expiration_dates(self):
        """Test that changing production date updates expiration dates."""
        initial_date = datetime(2024, 1, 1, 10, 0, 0)
        new_date = datetime(2024, 2, 1, 10, 0, 0)

        # Create lot with initial production date
        lot = self.env["stock.lot"].create(
            {
                "name": "TEST-LOT-002",
                "product_id": self.product_expiring.id,
                "production_date": initial_date,
            }
        )

        # Verify initial dates
        initial_expiration = lot.expiration_date
        self.assertEqual(initial_expiration, initial_date + timedelta(days=30))

        # Change production date
        lot.write({"production_date": new_date})

        # Verify dates are updated
        expected_expiration = new_date + timedelta(days=30)
        expected_use_date = expected_expiration - timedelta(days=7)
        expected_removal_date = expected_expiration - timedelta(days=3)
        expected_alert_date = expected_expiration - timedelta(days=10)

        self.assertEqual(lot.expiration_date, expected_expiration)
        self.assertEqual(lot.use_date, expected_use_date)
        self.assertEqual(lot.removal_date, expected_removal_date)
        self.assertEqual(lot.alert_date, expected_alert_date)

        # Ensure dates changed from initial
        self.assertNotEqual(lot.expiration_date, initial_expiration)

    def test_no_expiration_for_non_expiring_product(self):
        """Test that production date doesn't set expiration
        for non-expiring products."""
        production_date = datetime(2024, 1, 1, 10, 0, 0)

        # Create lot with non-expiring product
        lot = self.env["stock.lot"].create(
            {
                "name": "TEST-LOT-003",
                "product_id": self.product_non_expiring.id,
                "production_date": production_date,
            }
        )

        # Check that no expiration dates are set
        self.assertFalse(lot.expiration_date)
        self.assertFalse(lot.use_date)
        self.assertFalse(lot.removal_date)
        self.assertFalse(lot.alert_date)

    def test_no_production_date_no_expiration(self):
        """Test that lot without production date doesn't get expiration dates."""
        # Create lot without production date
        lot = self.env["stock.lot"].create(
            {
                "name": "TEST-LOT-004",
                "product_id": self.product_expiring.id,
            }
        )

        # Check that no expiration dates are set
        self.assertFalse(lot.expiration_date)
        self.assertFalse(lot.use_date)
        self.assertFalse(lot.removal_date)
        self.assertFalse(lot.alert_date)

    def test_bulk_creation_with_production_dates(self):
        """Test that bulk creation works with production dates."""
        production_date = datetime(2024, 1, 1, 10, 0, 0)

        # Create multiple lots with production dates
        lots = self.env["stock.lot"].create(
            [
                {
                    "name": "TEST-LOT-005",
                    "product_id": self.product_expiring.id,
                    "production_date": production_date,
                },
                {
                    "name": "TEST-LOT-006",
                    "product_id": self.product_expiring.id,
                    "production_date": production_date,
                },
            ]
        )

        # Check that all lots have expiration dates set
        expected_expiration = production_date + timedelta(days=30)
        for lot in lots:
            self.assertEqual(lot.expiration_date, expected_expiration)
            self.assertEqual(lot.use_date, expected_expiration - timedelta(days=7))
            self.assertEqual(lot.removal_date, expected_expiration - timedelta(days=3))
            self.assertEqual(lot.alert_date, expected_expiration - timedelta(days=10))
