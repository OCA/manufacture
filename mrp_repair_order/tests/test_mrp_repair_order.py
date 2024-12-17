# Copyright 2024 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase


class MRPRepairOrderTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mrp_order = cls.env["mrp.production"].create(
            [
                {
                    "product_id": cls.env.ref("product.product_delivery_01").id,
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
        self.assertEqual(self.mrp_order.repair_id.product_id, repair_order.product_id)
        self.assertEqual(self.mrp_order.repair_id.product_qty, repair_order.product_qty)
