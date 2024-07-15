from datetime import datetime

from odoo.tests.common import TransactionCase


class TestRepairOrder(TransactionCase):
    def setUp(self):
        super(TestRepairOrder, self).setUp()
        self.user = self.env["res.users"].create(
            {
                "name": "Test User",
                "login": "testuser",
                "password": "testpassword",
            }
        )
        self.product = self.env["product.product"].create(
            {"name": "Test Product", "type": "product", "list_price": 10.0}
        )
        self.repair_order = self.env["repair.order"].create(
            {
                "user_id": self.user.id,
                "product_id": self.product.id,
                "date_repair": datetime(2024, 7, 15, 10, 0, 0),
                "duration": 3.5,
            }
        )

    def test_repair_order_values(self):
        self.assertEqual(
            self.repair_order.user_id,
            self.user,
            "User ID should match the created user",
        )
        self.assertEqual(
            self.repair_order.date_repair,
            datetime(2024, 7, 15, 10, 0, 0),
            "Repair date should match the set value",
        )
        self.assertEqual(
            self.repair_order.duration,
            3.5,
            "Repair duration should match the set value",
        )
        self.assertEqual(
            self.repair_order.product_id,
            self.product,
            "Product ID should match the created product",
        )

    def test_default_user(self):
        repair_order = self.env["repair.order"].create(
            {
                "product_id": self.product.id,  # Include the product_id
                "date_repair": datetime(2024, 7, 15, 10, 0, 0),
                "duration": 3.5,
            }
        )
        self.assertEqual(
            repair_order.user_id,
            self.env.user,
            "Default user ID should match the current user",
        )
