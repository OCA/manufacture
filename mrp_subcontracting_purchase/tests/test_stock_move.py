from odoo.tests import Form, TransactionCase


class TestStockMove(TransactionCase):
    def setUp(self):
        super(TestStockMove, self).setUp()
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.product = self.env["product.product"].create(
            {
                "name": "Product no BoM",
                "type": "product",
            }
        )
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.product
        self.mo = mo_form.save()

        self.uom_kg = self.env.ref("uom.product_uom_kgm")
        self.warehouse = self.env["stock.warehouse"].search(
            [("lot_stock_id", "=", self.stock_location.id)], limit=1
        )
        self.picking01 = self.env["stock.move"].create(
            {
                "name": "mrp_move",
                "product_id": self.product.id,
                "product_uom": self.ref("uom.product_uom_unit"),
                "production_id": self.mo.id,
                "location_id": self.ref("stock.stock_location_stock"),
                "location_dest_id": self.ref("stock.stock_location_output"),
                "product_uom_qty": 0,
                "quantity_done": 0,
            }
        )

        self.subcontracor = self.env["res.partner"].create(
            {
                "name": "Subc Partner",
                "property_stock_subcontractor": self.ref("stock.stock_location_stock"),
            }
        )
        self.vendor = self.env["res.partner"].create({"name": "vendor #1"})

        dropship_subcontractor_route = self.env["stock.location.route"].search(
            [("name", "=", "Dropship Subcontractor on Order")]
        )

        self.product_component = self.env["product.product"].create(
            {
                "name": "Component",
                "type": "consu",
                "seller_ids": [(0, 0, {"name": self.vendor.id})],
                "route_ids": [(6, 0, dropship_subcontractor_route.ids)],
            }
        )
        self.env["stock.location"].create(
            {
                "name": "Super Location",
                "location_id": self.ref("stock.stock_location_stock"),
            }
        )

        self.customer_location = self.env.ref("stock.stock_location_customers")

    def test_get_subcontract_production(self):
        result = self.picking01._get_subcontract_production()
        self.assertFalse(result)

        self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "product_qty": 1,
                "type": "subcontract",
                "subcontractor_ids": [(6, 0, self.subcontracor.ids)],
                "bom_line_ids": [
                    (0, 0, {"product_id": self.product_component.id, "product_qty": 1})
                ],
            }
        )

        self.picking01.write(
            {
                "is_subcontract": True,
                "move_orig_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "orig_move",
                            "product_id": self.product.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "production_id": self.mo.id,
                            "location_id": self.ref("stock.stock_location_stock"),
                            "location_dest_id": self.ref("stock.stock_location_output"),
                            "product_uom_qty": 0,
                            "quantity_done": 0,
                        },
                    )
                ],
            }
        )
        picking_ship = self.env["stock.picking"].create(
            {
                "partner_id": self.env["res.partner"].create({"name": "A partner"}).id,
                "picking_type_id": self.warehouse.out_type_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        self.picking01.write(
            {
                "move_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_component.id,
                            "product_uom_id": self.uom_kg.id,
                            "picking_id": picking_ship.id,
                            "qty_done": 5,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.customer_location.id,
                        },
                    )
                ]
            }
        )
        result = self.picking01._get_subcontract_production()
        self.assertTrue(result)
        self.assertTrue(self.picking01.show_details_visible)
        self.assertTrue(self.picking01.show_subcontracting_details_visible)
        self.assertFalse(self.picking01.display_assign_serial)

        result = picking_ship._get_subcontract_production()
        self.assertFalse(result)
        result = picking_ship.action_view_subcontracting_source_purchase()
        self.assertEqual(result.get("res_model"), "purchase.order")
        self.assertEqual(result.get("type"), "ir.actions.act_window")
        self.assertEqual(
            result.get("name"), "Source PO of {}".format(picking_ship.name)
        )
        self.assertListEqual(result.get("domain"), [("id", "in", [])])
        self.assertEqual(result.get("view_mode"), "tree,form")
