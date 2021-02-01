# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestMrpMtoWithStock(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestMrpMtoWithStock, self).setUp(*args, **kwargs)
        self.repair_obj = self.env["repair.order"]
        self.repair_line_obj = self.env["repair.line"]
        self.product_obj = self.env["product.product"]
        self.move_obj = self.env["stock.move"]

        self.stock_location_stock = self.env.ref("stock.stock_location_stock")
        self.customer_location = self.env.ref("stock.stock_location_customers")
        self.refurbish_loc = self.env.ref("repair_refurbish.stock_location_refurbish")

        self.refurbish_product = self.product_obj.create(
            {"name": "Refurbished Awesome Screen", "type": "product"}
        )
        self.product = self.product_obj.create(
            {
                "name": "Awesome Screen",
                "type": "product",
                "refurbish_product_id": self.refurbish_product.id,
            }
        )
        self.material = self.product_obj.create({"name": "Materials", "type": "consu"})
        self.material2 = self.product_obj.create(
            {"name": "Materials", "type": "product"}
        )
        self._update_product_qty(self.product, self.stock_location_stock, 10.0)

    def _update_product_qty(self, product, location, quantity):
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Test Inventory",
                "product_ids": [(6, 0, product.ids)],
                "state": "confirm",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_qty": quantity,
                            "location_id": location.id,
                            "product_id": product.id,
                            "product_uom_id": product.uom_id.id,
                        },
                    )
                ],
            }
        )
        inventory.action_start()
        inventory.line_ids[0].write({"product_qty": quantity})
        inventory.action_validate()
        return quantity

    def test_01_repair_refurbish(self):
        """Tests that locations are properly set with a product to
        refurbish, then complete repair."""
        repair = self.repair_obj.create(
            {
                "product_id": self.product.id,
                "product_qty": 3.0,
                "product_uom": self.product.uom_id.id,
                "location_dest_id": self.customer_location.id,
                "location_id": self.stock_location_stock.id,
            }
        )
        repair.onchange_product_id()
        self.assertTrue(repair.to_refurbish)
        repair._onchange_to_refurbish()
        self.assertEqual(repair.refurbish_location_dest_id, self.customer_location)
        self.assertEqual(repair.location_dest_id, self.product.property_stock_refurbish)
        line = self.repair_line_obj.with_context(
            to_refurbish=repair.to_refurbish,
            refurbish_location_dest_id=repair.refurbish_location_dest_id,
        ).new(
            {
                "name": "consume stuff to repair",
                "repair_id": repair.id,
                "type": "add",
                "product_id": self.material.id,
                "product_uom": self.material.uom_id.id,
                "product_uom_qty": 1.0,
            }
        )
        line.onchange_product_id()
        line.onchange_operation_type()
        self.assertEqual(line.location_id, repair.location_id)
        self.assertEqual(line.location_dest_id, self.customer_location)
        # Complete repair:
        repair.action_validate()
        repair.action_repair_start()
        repair.action_repair_end()
        moves = self.move_obj.search([("reference", "=", repair.name)])
        self.assertEqual(len(moves), 2)
        for m in moves:
            self.assertEqual(m.state, "done")
            if m.product_id == self.product:
                self.assertEqual(m.location_id, self.stock_location_stock)
                self.assertEqual(m.location_dest_id, self.refurbish_loc)
                self.assertEqual(
                    m.mapped("move_line_ids.location_id"), self.stock_location_stock
                )
                self.assertEqual(
                    m.mapped("move_line_ids.location_dest_id"), self.refurbish_loc
                )
            elif m.product_id == self.refurbish_product:
                self.assertEqual(m.location_id, self.refurbish_loc)
                self.assertEqual(m.location_dest_id, self.customer_location)
                self.assertEqual(
                    m.mapped("move_line_ids.location_id"), self.refurbish_loc
                )
                self.assertEqual(
                    m.mapped("move_line_ids.location_dest_id"), self.customer_location
                )
            else:
                self.assertTrue(False, "Unexpected move.")

    def test_02_repair_no_refurbish(self):
        """Tests normal repairs does not fail and normal location for consumed
        material"""
        repair = self.repair_obj.create(
            {
                "product_id": self.product.id,
                "product_qty": 3.0,
                "product_uom": self.product.uom_id.id,
                "location_dest_id": self.customer_location.id,
                "to_refurbish": False,
                "location_id": self.stock_location_stock.id,
            }
        )

        line = self.repair_line_obj.with_context(
            to_refurbish=repair.to_refurbish,
            refurbish_location_dest_id=repair.refurbish_location_dest_id,
        ).create(
            {
                "name": "consume stuff to repair",
                "repair_id": repair.id,
                "type": "add",
                "product_id": self.material2.id,
                "product_uom": self.material2.uom_id.id,
                "product_uom_qty": 1.0,
                "price_unit": 50.0,
                "location_id": self.stock_location_stock.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        line.onchange_product_id()
        line.onchange_operation_type()
        # Complete repair:
        repair.action_validate()
        repair.action_repair_start()
        repair.action_repair_end()
        move = self.move_obj.search(
            [("product_id", "=", self.material2.id)], order="create_date desc", limit=1
        )[0]
        self.assertEqual(move.location_dest_id, self.customer_location)
