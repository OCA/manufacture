# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestMrpMtoWithStock(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.repair_obj = self.env["repair.order"]
        self.stock_move_obj = self.env["stock.move"]
        self.product_obj = self.env["product.product"]

        self.stock_location_stock = self.env.ref("stock.stock_location_stock")
        self.customer_location = self.env.ref("stock.stock_location_customers")
        self.scrap_location = self.env["stock.location"].search(
            [("scrap_location", "=", True)], limit=1
        )
        self.picking_type = self.env.ref("repair.picking_type_warehouse0_repair")
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
        self.env["stock.quant"].create(
            {
                "location_id": location.id,
                "product_id": self.product.id,
                "inventory_quantity_auto_apply": 10,
            }
        )
        return quantity

    def test_01_repair_refurbish(self):
        """Tests that locations are properly set with a product to
        refurbish, then complete repair."""
        repair = self.repair_obj.create(
            {
                "name": self.picking_type.sequence_id.next_by_id(),
                "product_id": self.product.id,
                "product_qty": 3.0,
                "product_uom": self.product.uom_id.id,
                "location_dest_id": self.customer_location.id,
                "location_id": self.stock_location_stock.id,
                "picking_type_id": self.picking_type.id,
                "to_refurbish": True,
            }
        )
        repair._onchange_product_id()
        self.assertTrue(repair.to_refurbish)
        repair._onchange_to_refurbish()
        self.assertEqual(repair.refurbish_location_dest_id, self.customer_location)
        self.assertEqual(repair.location_dest_id, self.product.property_stock_refurbish)
        line = self.stock_move_obj.with_context(
            to_refurbish=repair.to_refurbish,
            refurbish_location_dest_id=repair.refurbish_location_dest_id,
        ).new(
            {
                "name": "consume stuff to repair",
                "repair_id": repair.id,
                # "selection": "add",
                "product_id": self.material.id,
                "product_uom": self.material.uom_id.id,
                "quantity": 1.0,
            }
        )

        line._onchange_product_id()
        self.assertEqual(line.location_id, repair.location_id)
        self.assertEqual(line.location_dest_id, self.customer_location)
        # Complete repair:
        repair.action_validate()
        repair.action_repair_start()
        repair.action_repair_end()
        moves = self.stock_move_obj.search([("reference", "=", repair.name)])
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
                "name": self.picking_type.sequence_id.next_by_id(),
                "product_id": self.product.id,
                "product_qty": 3.0,
                "product_uom": self.product.uom_id.id,
                "location_dest_id": self.customer_location.id,
                "to_refurbish": False,
                "location_id": self.stock_location_stock.id,
                "picking_type_id": self.picking_type.id,
            }
        )

        line = self.stock_move_obj.with_context(
            to_refurbish=repair.to_refurbish,
            refurbish_location_dest_id=repair.refurbish_location_dest_id,
        ).create(
            {
                "name": "consume stuff to repair",
                "repair_id": repair.id,
                # "selection": "add",
                "product_id": self.material.id,
                "product_uom": self.material.uom_id.id,
                "quantity": 1.0,
                "price_unit": 50.0,
                "location_id": self.stock_location_stock.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        line._onchange_product_id()
        # Complete repair:
        repair.action_validate()
        repair.action_repair_start()
        repair.action_repair_end()
        move = self.stock_move_obj.search(
            [("product_id", "=", self.material2.id)], order="create_date desc", limit=1
        )[0]
        self.assertEqual(move.location_dest_id, self.scrap_location)
