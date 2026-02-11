# Copyright 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestMrpLotBatchPropagation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create products
        cls.product_batch = cls.env["product.template"].create(
            {
                "name": "Batch Product",
                "mrp_batch_propagate": True,
            }
        )
        cls.product_component = cls.env["product.template"].create(
            {
                "name": "Component",
            }
        )

        # Create BOM
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_batch.id,
                "product_qty": 1.0,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_tmpl_id": cls.product_component.id,
                            "product_qty": 2.0,
                        },
                    ),
                ],
            }
        )

        # Create manufacturing order
        cls.mrp_production = cls.env["mrp.production"].create(
            {
                "product_tmpl_id": cls.product_batch.id,
                "bom_id": cls.bom.id,
                "product_qty": 10.0,
            }
        )

    def test_batch_product_configuration(self):
        """Test batch product configuration on template and category"""
        # Test template level configuration
        self.assertTrue(self.product_batch.mrp_batch_propagate)
        self.assertTrue(self.product_batch.mrp_batch_propagate_computed)

        # Test category level configuration
        category = self.env["product.category"].create(
            {
                "name": "Batch Category",
                "mrp_batch_propagate": True,
            }
        )
        product_from_category = self.env["product.template"].create(
            {
                "name": "Product from Category",
                "categ_id": category.id,
            }
        )
        self.assertTrue(product_from_category.mrp_batch_propagate_computed)

    def test_batch_bom_on_finished_lot(self):
        """Test that batch BOM is set on finished lots for batch products"""
        # Create lots for components
        component_lot = self.env["stock.lot"].create(
            {
                "name": "COMP001",
                "product_id": self.product_component.product_variant_ids.id,
            }
        )

        # Assign component lots
        self.mrp_production.action_confirm()
        for move in self.mrp_production.move_raw_ids:
            move.move_line_ids.write({"lot_id": component_lot.id})

        # Mark production as done
        self.mrp_production.button_mark_done()

        # Check that finished lots have batch BOM
        finished_lots = self.mrp_production.move_finished_ids.move_line_ids.lot_id
        for lot in finished_lots:
            self.assertEqual(lot.batch_bom_id, self.bom)

    def test_batch_bom_ids_computation(self):
        """Test that batch_bom_ids is computed from consumed lots"""
        # Create a lot with batch BOM
        batch_bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product_component.id,
                "product_qty": 1.0,
            }
        )
        component_lot = self.env["stock.lot"].create(
            {
                "name": "COMP002",
                "product_id": self.product_component.product_variant_ids.id,
                "batch_bom_id": batch_bom.id,
            }
        )

        # Create second production that consumes the batch lot
        second_production = self.env["mrp.production"].create(
            {
                "product_tmpl_id": self.product_batch.id,
                "bom_id": self.bom.id,
                "product_qty": 5.0,
            }
        )

        second_production.action_confirm()
        for move in second_production.move_raw_ids:
            move.move_line_ids.write({"lot_id": component_lot.id})

        # Check that batch_bom_ids contains the batch BOM
        self.assertIn(batch_bom, second_production.batch_bom_ids)

    def test_no_batch_bom_for_non_batch_products(self):
        """Test that non-batch products don't get batch BOM on lots"""
        # Create non-batch product
        non_batch_product = self.env["product.template"].create(
            {
                "name": "Non Batch Product",
            }
        )

        # Create production for non-batch product
        non_batch_production = self.env["mrp.production"].create(
            {
                "product_tmpl_id": non_batch_product.id,
                "bom_id": self.bom.id,
                "product_qty": 5.0,
            }
        )

        non_batch_production.button_mark_done()

        # Check that finished lots don't have batch BOM
        finished_lots = non_batch_production.move_finished_ids.move_line_ids.lot_id
        for lot in finished_lots:
            self.assertFalse(lot.batch_bom_id)
