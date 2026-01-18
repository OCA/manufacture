# Copyright 2025 Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("-at_install", "post_install")
class TestMrpBomBatchSize(TransactionCase):
    def setUp(self):
        super().setUp()

        # Create test product
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
            }
        )

        # Create test BOM with batch size
        self.bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product.product_tmpl_id,
                "product_qty": 1.0,
                "enable_batch_size": True,
                "batch_size": 10.0,
            }
        )

        # Create warehouse and procurement rule
        self.warehouse = self.env["stock.warehouse"].search([], limit=1)
        self.location = self.warehouse.lot_stock_id

        # Create manufacturing rule
        self.rule = self.env["stock.rule"].create(
            {
                "name": "Manufacture Rule",
                "action": "manufacture",
                "location_id": self.location.id,
                "location_src_id": self.warehouse.wh_input_stock_loc.id,
                "procure_method": "make_to_order",
                "company_id": self.env.company.id,
            }
        )

    def test_batch_size_validation(self):
        """Test that batch size validation works correctly"""
        # Test negative batch size
        with self.assertRaises(ValidationError):
            self.bom.write({"batch_size": -5.0})

        # Test zero batch size
        with self.assertRaises(ValidationError):
            self.bom.write({"batch_size": 0.0})

        # Test positive batch size (should work)
        self.bom.write({"batch_size": 5.0})
        self.assertEqual(self.bom.batch_size, 5.0)

    def test_batch_size_disabled(self):
        """Test that batch size logic is disabled when enable_batch_size is False"""
        self.bom.write({"enable_batch_size": False})

        # Create procurement
        procurement = self.env["procurement.group"].Procurement(
            self.product,
            25.0,
            self.env.ref("uom.product_uom_unit"),
            self.location,
            "Test Procurement",
            "TEST",
            self.env.company,
            {"rule_id": self.rule},
        )

        # Run procurement - should create single MO without batch splitting
        self.rule.run([procurement])

        # Check that only one MO was created
        mos = self.env["mrp.production"].search([("product_id", "=", self.product.id)])
        self.assertEqual(len(mos), 1)
        self.assertEqual(mos.product_qty, 25.0)

    def test_batch_size_enabled(self):
        """Test that batch size logic works when enabled"""
        # Create procurement for 25 units, batch size is 10
        procurement = self.env["procurement.group"].Procurement(
            self.product,
            25.0,
            self.env.ref("uom.product_uom_unit"),
            self.location,
            "Test Procurement",
            "TEST",
            self.env.company,
            {"rule_id": self.rule},
        )

        # Run procurement - should create 3 MOs (10, 10, 5)
        self.rule.run([procurement])

        # Check that 3 MOs were created
        mos = self.env["mrp.production"].search([("product_id", "=", self.product.id)])
        self.assertEqual(len(mos), 3)

        # Check quantities
        quantities = sorted(mos.mapped("product_qty"))
        self.assertEqual(quantities, [5.0, 10.0, 10.0])

    def test_production_split_wizard(self):
        """Test that production split wizard respects batch size"""
        # Create a production order
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 25.0,
                "bom_id": self.bom.id,
            }
        )

        # Create split wizard
        wizard = self.env["mrp.production.split"].create(
            {
                "production_id": mo.id,
            }
        )

        # Check that max_batch_size is computed correctly
        self.assertEqual(wizard.max_batch_size, 10.0)

        # Check that num_splits is automatically calculated
        # (25 qty / 10 batch size = 3 splits)
        self.assertEqual(wizard.num_splits, 3)

        # Check that counter is also updated to match num_splits
        self.assertEqual(wizard.counter, 3)

        # Check that split details are properly populated (should be [10, 10, 5])
        split_details = wizard.production_detailed_vals_ids.mapped("quantity")
        expected_quantities = [10.0, 10.0, 5.0]
        self.assertEqual(len(split_details), 3)
        self.assertEqual(sorted(split_details), expected_quantities)

    def test_production_computed_qty_from_batch_size(self):
        """Test that production order gets batch size as computed quantity"""
        # Create production with batch size BoM
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "bom_id": self.bom.id,
                "product_qty": 5.0,  # Initial value
            }
        )

        # Check that product_qty is computed to batch size
        self.assertEqual(mo.product_qty, 10.0)

    def test_production_computed_qty_no_batch_size(self):
        """Test that production order uses normal logic when no batch size"""
        # Create production without batch size BoM
        bom_no_batch = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product.product_tmpl_id,
                "product_qty": 3.0,
                "enable_batch_size": False,
            }
        )

        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "bom_id": bom_no_batch.id,
                "product_qty": 5.0,
            }
        )

        # Check that product_qty is not changed (no batch size)
        self.assertEqual(mo.product_qty, 5.0)

    def test_production_computed_qty_bom_change(self):
        """Test that changing BoM updates quantity to batch size"""
        # Create production without batch size BoM
        bom_no_batch = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product.product_tmpl_id,
                "product_qty": 1.0,
                "enable_batch_size": False,
            }
        )

        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "bom_id": bom_no_batch.id,
                "product_qty": 5.0,
            }
        )

        # Change to BoM with batch size
        mo.bom_id = self.bom.id

        # Check that product_qty is updated to batch size
        self.assertEqual(mo.product_qty, 10.0)

    def test_production_split_wizard_batch_size_update(self):
        """Test that updating batch size triggers recalculation of split details"""
        # Create a production order
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 25.0,
                "bom_id": self.bom.id,
            }
        )

        # Create split wizard
        wizard = self.env["mrp.production.split"].create(
            {
                "production_id": mo.id,
            }
        )

        # Initial state: batch size 10, should create 3 splits [10, 10, 5]
        self.assertEqual(wizard.num_splits, 3)
        split_details = wizard.production_detailed_vals_ids.mapped("quantity")
        self.assertEqual(sorted(split_details), [5.0, 10.0, 10.0])

        # Update batch size to 8, should create 4 splits [8, 8, 8, 1]
        self.bom.batch_size = 8.0
        wizard._compute_max_batch_size()
        wizard._compute_num_splits()

        self.assertEqual(wizard.num_splits, 4)
        self.assertEqual(wizard.counter, 4)  # Counter should match num_splits
        split_details = wizard.production_detailed_vals_ids.mapped("quantity")
        self.assertEqual(sorted(split_details), [1.0, 8.0, 8.0, 8.0])
