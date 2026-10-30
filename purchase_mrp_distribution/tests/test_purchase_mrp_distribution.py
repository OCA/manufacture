# Copyright 2024 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import Form, TransactionCase


class TestPurchaseMrpDistribution(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["product.category"].create(
            {
                "name": "AVCO",
                "property_cost_method": "average",
            }
        )
        cls.product = cls.env["product.template"].create(
            {
                "name": "General product",
                "is_storable": True,
                "categ_id": cls.category.id,
            }
        )
        cls.subproduct_1 = cls.env["product.template"].create(
            {
                "name": "Product 1",
                "is_storable": True,
                "categ_id": cls.category.id,
            }
        )
        cls.subproduct_2 = cls.env["product.template"].create(
            {
                "name": "Product 2",
                "is_storable": True,
                "categ_id": cls.category.id,
            }
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product.id,
                "type": "distribution",
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.subproduct_1.product_variant_id.id,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.subproduct_2.product_variant_id.id,
                        }
                    ),
                ],
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Partner",
            }
        )

    def _create_po_picking(self):
        purchase_form = Form(self.env["purchase.order"])
        purchase_form.partner_id = self.partner
        with purchase_form.order_line.new() as line_form:
            line_form.product_id = self.product.product_variant_id
            line_form.product_qty = 6
            line_form.price_unit = 2
        purchase = purchase_form.save()
        purchase.button_confirm()
        return purchase, purchase.picking_ids

    def test_distribute_process(self):
        purchase, picking = self._create_po_picking()
        wiz_action = picking.move_ids.action_open_distribution_wizard()
        wiz = (
            self.env["stock.move.distribution.wiz"]
            .with_context(**wiz_action["context"])
            .create({})
        )
        self.assertIn(self.subproduct_1.product_variant_id, wiz.line_ids.product_id)
        self.assertIn(self.subproduct_2.product_variant_id, wiz.line_ids.product_id)
        wiz.line_ids.quantity = 3
        wiz.button_distribute_qty()
        self.assertEqual(len(picking.move_ids), 1)
        self.assertEqual(len(picking.move_ids.move_line_ids), 2)
        for sml in picking.move_ids.move_line_ids:
            self.assertEqual(sml.quantity, 3)
        original_move = picking.move_ids
        picking.button_validate()
        self.assertEqual(len(picking.move_ids), 3)
        self.assertEqual(original_move.state, "cancel")
        self.assertIn(self.subproduct_1.product_variant_id, picking.move_ids.product_id)
        self.assertIn(self.subproduct_2.product_variant_id, picking.move_ids.product_id)
        self.assertEqual(purchase.order_line.qty_received, 6)
        # Each distributed product is valued on its own move, but accounted for
        # in the purchase line of the generic product.
        distributed_moves = picking.move_ids - original_move
        self.assertEqual(len(distributed_moves), 2)
        for move in distributed_moves:
            self.assertTrue(move.is_valued)
            self.assertEqual(move.quantity, 3)
            self.assertEqual(move.value, 6)
