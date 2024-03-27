# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestStockRepairWarehouse(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockRepairWarehouse, cls).setUpClass()

        cls.warehouse_obj = cls.env["stock.warehouse"]
        cls.product_obj = cls.env["product.product"]

        cls.product_1 = cls.product_obj.create(
            {
                "name": "Product 1",
                "type": "product",
            }
        )

        cls.warehouse_1 = cls.warehouse_obj.create(
            {
                "name": "Test Warehouse",
                "code": "TWH",
                "repair_steps": "1_step",
            }
        )

    def test_01_warehouse_creation(self):
        self.assertEqual(self.warehouse_1.repair_steps, "1_step")

    def test_02_update_repair_steps(self):
        self.warehouse_1.repair_steps = "2_steps"

        self.assertEqual(self.warehouse_1.repair_steps, "2_steps")
        self.assertTrue(self.warehouse_1.add_c_type_id.active)
        self.assertFalse(self.warehouse_1.remove_c_type_id.active)
        self.assertTrue(self.warehouse_1.repair_route_id.active)

    def test_03_update_repair_steps_to_3_steps(self):
        self.warehouse_1.repair_steps = "3_steps"

        self.assertEqual(self.warehouse_1.repair_steps, "3_steps")
        self.assertTrue(self.warehouse_1.add_c_type_id.active)
        self.assertTrue(self.warehouse_1.remove_c_type_id.active)
        self.assertTrue(self.warehouse_1.repair_route_id.active)

    def test_04_reverse_and_update_repair_steps(self):
        self.warehouse_1.repair_steps = "1_step"
        self.warehouse_1.repair_steps = "2_steps"
        self.assertEqual(self.warehouse_1.repair_steps, "2_steps")
        self.assertTrue(self.warehouse_1.add_c_type_id.active)
        self.assertFalse(self.warehouse_1.remove_c_type_id.active)
        self.assertTrue(self.warehouse_1.repair_route_id.active)
        add_rule = self.env["stock.rule"].search(
            [
                ("picking_type_id", "=", self.warehouse_1.add_c_type_id.id),
                ("route_id", "=", self.warehouse_1.repair_route_id.id),
            ]
        )
        self.assertTrue(add_rule.active)

        remove_rule = self.env["stock.rule"].search(
            [
                ("picking_type_id", "=", self.warehouse_1.remove_c_type_id.id),
                ("route_id", "=", self.warehouse_1.repair_route_id.id),
            ]
        )
        self.assertFalse(remove_rule)

        self.warehouse_1.repair_steps = "3_steps"
        self.assertEqual(self.warehouse_1.repair_steps, "3_steps")
        self.assertTrue(self.warehouse_1.add_c_type_id.active)
        self.assertTrue(self.warehouse_1.remove_c_type_id.active)
        self.assertTrue(self.warehouse_1.repair_route_id.active)
        add_rule = self.env["stock.rule"].search(
            [
                ("picking_type_id", "=", self.warehouse_1.add_c_type_id.id),
                ("route_id", "=", self.warehouse_1.repair_route_id.id),
            ]
        )
        self.assertTrue(add_rule.active)
        remove_rule = self.env["stock.rule"].search(
            [
                ("picking_type_id", "=", self.warehouse_1.remove_c_type_id.id),
                ("route_id", "=", self.warehouse_1.repair_route_id.id),
            ]
        )
        self.assertTrue(remove_rule.active)

        self.warehouse_1.repair_steps = "2_steps"
        self.assertEqual(self.warehouse_1.repair_steps, "2_steps")
        self.assertTrue(self.warehouse_1.add_c_type_id.active)
        self.assertFalse(self.warehouse_1.remove_c_type_id.active)
        self.assertTrue(self.warehouse_1.repair_route_id.active)
        add_rule = self.env["stock.rule"].search(
            [
                ("picking_type_id", "=", self.warehouse_1.add_c_type_id.id),
                ("route_id", "=", self.warehouse_1.repair_route_id.id),
            ]
        )
        self.assertTrue(add_rule.active)

        remove_rule = self.env["stock.rule"].search(
            [
                ("picking_type_id", "=", self.warehouse_1.remove_c_type_id.id),
                ("route_id", "=", self.warehouse_1.repair_route_id.id),
            ]
        )
        self.assertFalse(remove_rule)

        self.warehouse_1.repair_steps = "1_step"
        self.assertFalse(self.warehouse_1.add_c_type_id.active)
        self.assertFalse(self.warehouse_1.remove_c_type_id.active)
        self.assertFalse(self.warehouse_1.repair_route_id.active)
