# Copyright 2023 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import common


class TestMrpPrimecontractorRawMaterial(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        mto_route = cls.env.ref("stock.route_warehouse0_mto")
        mto_route.active = True
        cls.product = cls.env["product.product"].create(
            {
                "name": "Manufactured product",
                "type": "product",
                "route_ids": [
                    (4, cls.env.ref("mrp.route_warehouse0_manufacture").id),
                    (4, mto_route.id),
                ],
            }
        )
        cls.primecontractor_product = cls.env["product.product"].create(
            {
                "name": "Raw material product from prime contractor",
                "type": "product",
            }
        )
        cls.normalproduct = cls.env["product.product"].create(
            {
                "name": "Raw material product from stock",
                "type": "product",
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Prime Contractor"})
        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)

        cls.env.ref("product.product_product_4").route_ids |= mto_route

        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.primecontractor_product.id,
                            "product_qty": 1,
                            "primecontractor_raw_material": True,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.normalproduct.id,
                            "product_qty": 1,
                        },
                    ),
                ],
            }
        )

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 1,
                        },
                    ),
                ],
            }
        )

    def test_mrp_primecontractor_raw_material_activate(self):
        self.assertFalse(self.warehouse.primecontractor_view_location_id)
        self.assertFalse(self.warehouse.primecontractor_pull_id)
        self.assertFalse(self.warehouse.primecontractor_in_type_id)

        self.warehouse.write({"primecontractor_raw_material": True})

        self.assertTrue(self.warehouse.primecontractor_view_location_id)
        self.assertTrue(self.warehouse.primecontractor_pull_id)
        self.assertTrue(self.warehouse.primecontractor_in_type_id)

        self.assertTrue(self.warehouse.primecontractor_view_location_id.active)
        self.assertTrue(self.warehouse.primecontractor_pull_id.active)
        self.assertTrue(self.warehouse.primecontractor_in_type_id.active)

    def test_mrp_primecontractor_raw_material_deactivate(self):
        self.warehouse.write({"primecontractor_raw_material": True})
        self.warehouse.write({"primecontractor_raw_material": False})

        self.assertTrue(self.warehouse.primecontractor_view_location_id)
        self.assertTrue(self.warehouse.primecontractor_pull_id)
        self.assertTrue(self.warehouse.primecontractor_in_type_id)

        # Rule is disabled
        self.assertFalse(self.warehouse.primecontractor_pull_id.active)

    def test_mrp_primecontractor_raw_material_create_with(self):
        warehouse = self.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse",
                "code": "TEST",
                "primecontractor_raw_material": True,
            }
        )

        self.assertTrue(warehouse.primecontractor_raw_material)
        self.assertTrue(warehouse.primecontractor_view_location_id)
        self.assertTrue(warehouse.primecontractor_pull_id)
        self.assertTrue(warehouse.primecontractor_in_type_id)

    def test_mrp_primecontractor_raw_material_create_without(self):
        warehouse = self.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse",
                "code": "TEST",
                "primecontractor_raw_material": False,
            }
        )

        self.assertFalse(warehouse.primecontractor_raw_material)
        self.assertFalse(warehouse.primecontractor_view_location_id.active)
        self.assertFalse(warehouse.primecontractor_pull_id.active)

    def test_mrp_primecontractor_raw_material_procurement_group(self):
        self.warehouse.write({"primecontractor_raw_material": True})

        primecontractor_location = self.env["stock.location"].create(
            {
                "name": "Prime Contractor Location",
                "location_id": self.warehouse.primecontractor_view_location_id.id,
                "primecontractor_id": self.partner.id,
            }
        )
        self.assertTrue(primecontractor_location.primecontractor_procurement_group_id)

    def test_mrp_primecontractor_raw_material_no_primecontractor_location(self):
        self.warehouse.write({"primecontractor_raw_material": True})
        with self.assertRaises(Exception):
            self.sale_order.action_confirm()

    def test_mrp_primecontractor_raw_material_order_manufactured_product(self):
        self.warehouse.write({"primecontractor_raw_material": True})

        primecontractor_location = self.env["stock.location"].create(
            {
                "name": "Prime Contractor Location",
                "location_id": self.warehouse.primecontractor_view_location_id.id,
                "primecontractor_id": self.partner.id,
            }
        )

        self.sale_order.action_confirm()
        self.assertEqual(self.sale_order.production_count, 1)
        production = self.sale_order.production_ids
        primecontractor_product_move = production.move_raw_ids.filtered(
            lambda m: m.product_id == self.primecontractor_product
        )
        self.assertTrue(primecontractor_product_move)

        self.assertEqual(
            primecontractor_product_move.location_id, primecontractor_location
        )

    def test_mrp_primecontractor_raw_material_orderpoint_restock_with_rule(
        self,
    ):
        self.warehouse.write({"primecontractor_raw_material": True})
        primecontractor_location = self.env["stock.location"].create(
            {
                "name": "Prime Contractor Location",
                "location_id": self.warehouse.primecontractor_view_location_id.id,
                "primecontractor_id": self.partner.id,
            }
        )
        self.assertTrue(primecontractor_location.primecontractor_procurement_group_id)

        self.other_partner = self.env["res.partner"].create(
            {"name": "Other Prime Contractor"}
        )
        other_partner_prime_contractor_location = self.env["stock.location"].create(
            {
                "name": "Other Prime Contractor Location",
                "location_id": self.warehouse.primecontractor_view_location_id.id,
                "primecontractor_id": self.other_partner.id,
            }
        )
        other_procurement_group = (
            other_partner_prime_contractor_location.primecontractor_procurement_group_id
        )
        self.assertTrue(other_procurement_group)
        self.assertNotEqual(
            primecontractor_location.primecontractor_procurement_group_id,
            other_procurement_group,
        )
        self.assertEqual(
            primecontractor_location.primecontractor_procurement_group_id.partner_id,
            self.partner,
        )
        self.assertEqual(
            other_procurement_group.partner_id,
            self.other_partner,
        )
        orderpoint_form = common.Form(self.env["stock.warehouse.orderpoint"])
        orderpoint_form.product_id = self.primecontractor_product
        orderpoint_form.location_id = primecontractor_location
        orderpoint_form.product_min_qty = 0.0
        orderpoint_form.product_max_qty = 4.0
        orderpoint = orderpoint_form.save()
        self.assertEqual(
            orderpoint.group_id,
            primecontractor_location.primecontractor_procurement_group_id,
        )
        self.assertEqual(orderpoint.qty_to_order, 0.0)
        test_move = self.env["stock.move"].create(
            {
                "name": "Test out move",
                "location_id": primecontractor_location.id,
                "location_dest_id": self.warehouse.lot_stock_id.id,
                "product_id": self.primecontractor_product.id,
                "product_uom_qty": 3.0,
                "product_uom": self.primecontractor_product.uom_id.id,
                "company_id": orderpoint.company_id.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )
        test_move._action_confirm()

        self.assertEqual(orderpoint.qty_to_order, 7.0)
        orderpoint._procure_orderpoint_confirm(company_id=orderpoint.company_id)
        prm_picking = (
            self.env["stock.move"]
            .search(
                [
                    ("product_id", "=", self.primecontractor_product.id),
                ]
            )
            .picking_id
            - test_move.picking_id
        )
        self.assertEqual(prm_picking.partner_id, self.partner)
        self.assertEqual(
            prm_picking.location_id, self.env.ref("stock.stock_location_suppliers")
        )
        self.assertEqual(prm_picking.location_dest_id, primecontractor_location)
        self.assertEqual(
            prm_picking.picking_type_id, self.warehouse.primecontractor_in_type_id
        )
        self.assertEqual(
            prm_picking.group_id,
            primecontractor_location.primecontractor_procurement_group_id,
        )
        self.assertEqual(len(prm_picking.move_lines), 1)

    def test_mrp_primecontractor_raw_material_restock_on_order_manufactured(
        self,
    ):
        self.warehouse.write({"primecontractor_raw_material": True})
        # Create prime contractor locations
        primecontractor_location = self.env["stock.location"].create(
            {
                "name": "Prime Contractor Location",
                "location_id": self.warehouse.primecontractor_view_location_id.id,
                "primecontractor_id": self.partner.id,
            }
        )
        self.other_partner = self.env["res.partner"].create(
            {"name": "Other Prime Contractor"}
        )
        self.env["stock.location"].create(
            {
                "name": "Other Prime Contractor Location",
                "location_id": self.warehouse.primecontractor_view_location_id.id,
                "primecontractor_id": self.other_partner.id,
            }
        )

        # Create orderpoint to restock prime contractor location
        orderpoint_form = common.Form(self.env["stock.warehouse.orderpoint"])
        orderpoint_form.product_id = self.primecontractor_product
        orderpoint_form.location_id = primecontractor_location
        orderpoint_form.product_min_qty = 0.0
        orderpoint_form.product_max_qty = 10.0
        orderpoint_form.save()

        self.assertFalse(
            self.env["stock.picking"].search(
                [
                    (
                        "picking_type_id",
                        "=",
                        self.warehouse.primecontractor_in_type_id.id,
                    ),
                ]
            )
        )

        # Confirm sale order
        self.sale_order.action_confirm()

        prm_picking = self.env["stock.picking"].search(
            [
                ("picking_type_id", "=", self.warehouse.primecontractor_in_type_id.id),
            ]
        )
        # There is now a restocking picking
        self.assertEqual(len(prm_picking), 1)
        self.assertEqual(prm_picking.partner_id, self.partner)
        self.assertEqual(
            prm_picking.location_id, self.env.ref("stock.stock_location_suppliers")
        )
        self.assertEqual(prm_picking.location_dest_id, primecontractor_location)
        self.assertEqual(
            prm_picking.picking_type_id, self.warehouse.primecontractor_in_type_id
        )
        self.assertEqual(
            prm_picking.group_id,
            primecontractor_location.primecontractor_procurement_group_id,
        )
        self.assertEqual(len(prm_picking.move_lines), 1)
        self.assertEqual(
            prm_picking.move_lines.product_id, self.primecontractor_product
        )
        self.assertEqual(prm_picking.move_lines.product_uom_qty, 11.0)
        self.assertEqual(
            prm_picking.move_lines.location_id,
            self.env.ref("stock.stock_location_suppliers"),
        )
        self.assertEqual(
            prm_picking.move_lines.location_dest_id, primecontractor_location
        )
