# Copyright (C) 2022 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo.tests.common import TransactionCase


class TestRepairTransfer(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestRepairTransfer, self).setUp(*args, **kwargs)

        # First of all we create a repair to work with
        self.repair_r1 = self.env.ref("repair.repair_r1")
        self.repair_r2 = self.env.ref("repair.repair_r1")

        # Now we will create a destination location
        self.stock_location_destination = self.env["stock.location"].create(
            {"name": "Destination Locations", "usage": "internal"}
        )

        # Let's add some stock
        self.env["stock.quant"].create(
            {
                "product_id": self.repair_r1.product_id.id,
                "location_id": self.repair_r1.location_id.id,
                "quantity": 1.0,
            }
        )

        # Create a product with lot/serial tracking
        product_with_lot = self.env["product.product"].create(
            {
                "name": "Product with lot tracking",
                "type": "product",
                "tracking": "lot",
                "list_price": 10.0,
                "categ_id": self.env.ref("product.product_category_all").id,
            }
        )
        lot_id = self.env["stock.production.lot"].create(
            {
                "name": "LOT0001",
                "product_id": product_with_lot.id,
                "company_id": self.env.company.id,
            }
        )
        # Let's add some stock
        self.env["stock.quant"].create(
            {
                "product_id": product_with_lot.id,
                "lot_id": lot_id.id,
                "location_id": self.repair_r2.location_id.id,
                "quantity": 1.0,
            }
        )
        self.repair_r2.write({"lot_id": lot_id.id, "product_id": product_with_lot.id})

    def test_repair_transfer_1(self):

        # Validate the repair order
        self.repair_r1.action_validate()
        self.assertEqual(self.repair_r1.state, "confirmed")

        self.repair_r1.action_assign()
        self.assertEqual(self.repair_r1.move_id.state, "assigned")

        self.repair_r1.action_repair_start()
        self.assertEqual(self.repair_r1.state, "under_repair")

        self.repair_r1.action_repair_end()
        self.assertEqual(self.repair_r1.state, "done")

        transfer_repair_wizard = self.env["repair.move.transfer"].create(
            {
                "repair_order_id": self.repair_r1.id,
                "quantity": 1.0,
                "location_dest_id": self.stock_location_destination.id,
            }
        )
        transfer_repair_wizard.action_create_transfer()

        self.assertEqual(len(self.repair_r1.picking_ids), 1)

    def test_repair_transfer_2(self):

        # Validate the repair order
        self.repair_r2.action_validate()
        self.assertEqual(self.repair_r2.state, "confirmed")

        self.repair_r2.action_assign()
        self.assertEqual(self.repair_r2.move_id.state, "assigned")

        self.repair_r2.action_repair_start()
        self.assertEqual(self.repair_r2.state, "under_repair")

        self.repair_r2.action_repair_end()
        self.assertEqual(self.repair_r2.state, "done")

        transfer_repair_wizard = self.env["repair.move.transfer"].create(
            {
                "repair_order_id": self.repair_r2.id,
                "quantity": 1.0,
                "location_dest_id": self.stock_location_destination.id,
            }
        )
        transfer_repair_wizard.action_create_transfer()
        self.assertEqual(len(self.repair_r2.picking_ids), 1)

        move_line = self.repair_r2.picking_ids.mapped("move_lines").mapped(
            "move_line_ids"
        )[0]
        self.assertEqual(move_line.lot_id.name, "LOT0001")
