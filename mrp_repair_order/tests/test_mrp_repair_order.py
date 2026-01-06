# Copyright 2024 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase


class MRPRepairOrderTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            [
                {
                    "name": "New Product",
                    "type": "consu",
                }
            ]
        )
        cls.mrp_order = cls.env["mrp.production"].create(
            [
                {
                    "product_id": cls.product.id,
                    "product_qty": 2,
                }
            ]
        )

    def test_create_repair_order_from_mrp(self):
        repair_form = Form(
            self.env["repair.order"].with_context(
                default_mrp_id=self.mrp_order.id,
                default_product_qty=self.mrp_order.product_qty,
                default_product_id=self.mrp_order.product_id.id,
                default_mrp_ids=[self.mrp_order.id],
            )
        )
        repair_order = repair_form.save()
        self.assertEqual(self.mrp_order.repair_id, repair_order)
        self.assertEqual(self.mrp_order, repair_order.mrp_ids)
        self.assertEqual(self.mrp_order.product_id, repair_order.product_id)
        self.assertEqual(self.mrp_order.product_qty, repair_order.product_qty)

        action_mrp = self.mrp_order.action_view_mrp_production_repair_orders()
        self.assertEqual(action_mrp["res_model"], "repair.order")
        self.assertEqual(action_mrp["res_id"], repair_order.id)

        action_repair = repair_order.action_view_repair_manufacturing_order()
        self.assertEqual(action_repair["res_model"], "mrp.production")
        self.assertEqual(action_repair["res_id"], self.mrp_order.id)

    def test_action_create_repair_order_from_mrp(self):
        action = self.mrp_order.action_create_repair_order()
        self.assertEqual(
            self.mrp_order.product_id.id, action["context"]["default_product_id"]
        )
        self.assertEqual(
            self.mrp_order.product_qty, action["context"]["default_product_qty"]
        )
        self.assertEqual([self.mrp_order.id], action["context"]["default_mrp_ids"])
