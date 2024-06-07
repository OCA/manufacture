# Copyright 2021 Forgeflow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo.tests import common


class TestMrpKitDropShip(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dropship_route = cls.env.ref("stock_dropshipping.route_drop_shipping")
        cls.buy_route = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test mrp_sale_info product",
                "type": "product",
                "route_ids": [(4, cls.dropship_route.id), (4, cls.buy_route.id)],
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Test kit component 1", "type": "consu"}
        )
        cls.product_3 = cls.env["product.product"].create(
            {"name": "Test kit component 2", "type": "consu"}
        )
        cls.bom = cls.env["mrp.bom"].create(
            {"product_tmpl_id": cls.product.product_tmpl_id.id, "type": "phantom"}
        )
        cls.env["mrp.bom.line"].create(
            {"bom_id": cls.bom.id, "product_id": cls.product_2.id, "product_qty": 2}
        )
        cls.env["mrp.bom.line"].create(
            {"bom_id": cls.bom.id, "product_id": cls.product_3.id, "product_qty": 2}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test client"})
        cls.vendor = cls.env["res.partner"].create({"name": "Test vendor"})

        cls.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_id": cls.product.id,
                "name": cls.vendor.id,
            }
        )

    def test_procure(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 1,
                            "route_id": self.dropship_route.id,
                        },
                    ),
                ],
            }
        )
        sale_order.action_confirm()
        self.assertFalse(
            sale_order.picking_ids,
            "No pickings should have been created out of the " "sales order.",
        )
        purchase = self.env["purchase.order"].search(
            [("partner_id", "=", self.vendor.id)]
        )
        self.assertTrue(purchase, "an RFQ should have been created by the scheduler")
        purchase.button_confirm()
        move_line = self.env["stock.move.line"].search(
            [
                (
                    "location_dest_id",
                    "=",
                    self.env.ref("stock.stock_location_customers").id,
                ),
                ("product_id", "=", self.product_2.id),
            ]
        )
        # The stock move is created for the components
        self.assertEquals(len(move_line), 1)
        self.assertEquals(
            len(move_line.ids), 1, "There should be exactly one move line"
        )
        purchase.picking_ids.move_lines.write({"quantity_done": 2})
        purchase.picking_ids.button_validate()
        self.assertEquals(sale_order.order_line[0].qty_delivered, 1)
