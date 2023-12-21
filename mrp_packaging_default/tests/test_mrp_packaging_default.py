# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import Command
from odoo.tests.common import Form

from odoo.addons.mrp.tests.common import TestMrpCommon


class MrpPackagingDefaultCase(TestMrpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Enable product packaging
        cls.env.ref("base.group_user")._apply_group(
            cls.env.ref("product.group_stock_packaging")
        )
        # Sandwich ingredients
        cls.tomato_product = cls.env["product.product"].create(
            {
                "name": "Tomato",
                "type": "product",
                "list_price": 5.0,
                "categ_id": cls.product_category.id,
                "uom_id": cls.env.ref("uom.product_uom_kgm").id,
                "uom_po_id": cls.env.ref("uom.product_uom_kgm").id,
                "packaging_ids": [
                    Command.create({"name": "Box", "qty": 3}),
                    Command.create({"name": "Unit", "qty": 0.2}),
                    Command.create({"name": "Slice", "qty": 0.05}),
                ],
            }
        )
        cls.lettuce_product = cls.env["product.product"].create(
            {
                "name": "Lettuce",
                "type": "product",
                "list_price": 1.0,
                "categ_id": cls.product_category.id,
                "uom_id": cls.env.ref("uom.product_uom_kgm").id,
                "uom_po_id": cls.env.ref("uom.product_uom_kgm").id,
                "packaging_ids": [
                    Command.create({"name": "Leaf", "qty": 0.05}),
                ],
            }
        )
        cls.bread_product = cls.env["product.product"].create(
            {
                "name": "Bread",
                "type": "product",
                "list_price": 3.0,
                "categ_id": cls.product_category.id,
                "uom_id": cls.env.ref("uom.product_uom_kgm").id,
                "uom_po_id": cls.env.ref("uom.product_uom_kgm").id,
                "packaging_ids": [
                    Command.create({"name": "Slice", "qty": 0.1}),
                ],
            }
        )

    def create_sandwich(self, cooked):
        """Create a sandwich product and its BoMs.

        If the sandwich is cooked, then we sell it as a manufactured product.

        Otherwise, it's a DIY sandwich; we sell the ingredients and you cook it
        yourself.
        """
        sandwich = self.env["product.product"].create(
            {
                "name": "Sandwich",
                "type": "product" if cooked else "consu",
                "list_price": 10.0 if cooked else 7.0,
                "categ_id": self.product_category.id,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
                "route_ids": [
                    Command.link(self.warehouse_1.manufacture_pull_id.route_id.id)
                ],
            }
        )
        bom_f = Form(self.env["mrp.bom"])
        bom_f.product_tmpl_id = sandwich.product_tmpl_id
        bom_f.type = "normal" if cooked else "phantom"
        with bom_f.bom_line_ids.new() as line_f:
            line_f.product_id = self.tomato_product
            self.assertEqual(line_f.product_packaging_id.name, "Box")
            self.assertEqual(line_f.product_packaging_qty, 1)
            self.assertEqual(line_f.product_qty, 3)
            line_f.product_packaging_id = self.tomato_product.packaging_ids[2]
            line_f.product_packaging_qty = 2
            self.assertEqual(line_f.product_packaging_id.name, "Slice")
            self.assertEqual(line_f.product_qty, 0.1)
        with bom_f.bom_line_ids.new() as line_f:
            line_f.product_id = self.lettuce_product
            self.assertEqual(line_f.product_packaging_id.name, "Leaf")
            self.assertEqual(line_f.product_packaging_qty, 1)
            self.assertEqual(line_f.product_qty, 0.05)
            line_f.product_packaging_qty = 4
            self.assertEqual(line_f.product_qty, 0.2)
        with bom_f.bom_line_ids.new() as line_f:
            line_f.product_id = self.bread_product
            self.assertEqual(line_f.product_packaging_id.name, "Slice")
            self.assertEqual(line_f.product_packaging_qty, 1)
            self.assertEqual(line_f.product_qty, 0.1)
            line_f.product_packaging_qty = 2
            self.assertEqual(line_f.product_qty, 0.2)
        bom_f.save()
        return sandwich

    def test_deliver_diy_sandwich(self):
        """Deliver a DIY sandwich.

        To deliver a sandwich, we would usually create a sale order. However,
        `sale` is not among this module's dependencies, so we create the
        picking directly.

        In product kits, the standard behavior es that when you confirm the
        picking, the system replaces the kit with its components, linked to
        each BoM line.

        Here we just exercise that behavior and assert that the packaging data
        matches the one that comes from the BoM.
        """
        sandwich = self.create_sandwich(cooked=False)
        picking_f = Form(self.env["stock.picking"].with_user(self.user_stock_user))
        picking_f.partner_id = self.partner_1
        picking_f.picking_type_id = self.warehouse_1.out_type_id
        with picking_f.move_ids_without_package.new() as move_f:
            move_f.product_id = sandwich
            move_f.product_uom_qty = 2
        picking = picking_f.save()
        picking.action_confirm()
        self.assertRecordValues(
            picking.move_ids_without_package,
            [
                {
                    "bom_line_id": sandwich.bom_ids[0].bom_line_ids[0].id,
                    "description_bom_line": "Sandwich - 1/3",
                    "product_id": self.tomato_product.id,
                    "product_packaging_id": self.tomato_product.packaging_ids[2].id,
                    "product_packaging_qty": 2.0,
                    "product_uom": self.env.ref("uom.product_uom_kgm").id,
                    "product_uom_qty": 0.1,
                },
                {
                    "bom_line_id": sandwich.bom_ids[0].bom_line_ids[1].id,
                    "description_bom_line": "Sandwich - 2/3",
                    "product_id": self.lettuce_product.id,
                    "product_packaging_id": self.lettuce_product.packaging_ids[0].id,
                    "product_packaging_qty": 4.0,
                    "product_uom": self.env.ref("uom.product_uom_kgm").id,
                    "product_uom_qty": 0.2,
                },
                {
                    "bom_line_id": sandwich.bom_ids[0].bom_line_ids[2].id,
                    "description_bom_line": "Sandwich - 3/3",
                    "product_id": self.bread_product.id,
                    "product_packaging_id": self.bread_product.packaging_ids[0].id,
                    "product_packaging_qty": 2,
                    "product_uom": self.env.ref("uom.product_uom_kgm").id,
                    "product_uom_qty": 0.2,
                },
            ],
        )

    def test_auto_procure_cooked_sandwich(self):
        """Procure a cooked sandwich.

        This sandwich is a manufactured product. It has reordering rules, so
        the procurement scheduler will create a manufacturing order.

        We will just exercise that scenario and make sure the packaging data in
        the manufacturing order matches the one in the BoM.
        """
        sandwich = self.create_sandwich(cooked=True)
        # Define a reordering rule for the cooked sandwich
        rule_f = Form(self.env["stock.warehouse.orderpoint"])
        rule_f.product_id = sandwich
        rule_f.product_min_qty = 4
        rule_f.product_max_qty = 10
        rule_f.save()
        # Run the stock scheduler
        self.env["procurement.group"].run_scheduler()
        # Check the created manufacturing order
        mo = self.env["mrp.production"].search([("product_id", "=", sandwich.id)])
        self.assertEqual(mo.state, "confirmed")
        self.assertEqual(mo.qty_producing, 0)
        self.assertEqual(mo.product_qty, 10)
        self.assertEqual(mo.bom_id, sandwich.bom_ids)
        self.assertRecordValues(
            mo.move_raw_ids,
            [
                {
                    "bom_line_id": sandwich.bom_ids[0].bom_line_ids[0].id,
                    "product_id": self.tomato_product.id,
                    "product_packaging_id": self.tomato_product.packaging_ids[2].id,
                    "product_packaging_qty": 2.0,
                    "product_uom": self.env.ref("uom.product_uom_kgm").id,
                    "product_uom_qty": 0.1,
                },
                {
                    "bom_line_id": sandwich.bom_ids[0].bom_line_ids[1].id,
                    "product_id": self.lettuce_product.id,
                    "product_packaging_id": self.lettuce_product.packaging_ids[0].id,
                    "product_packaging_qty": 4.0,
                    "product_uom": self.env.ref("uom.product_uom_kgm").id,
                    "product_uom_qty": 0.2,
                },
                {
                    "bom_line_id": sandwich.bom_ids[0].bom_line_ids[2].id,
                    "product_id": self.bread_product.id,
                    "product_packaging_id": self.bread_product.packaging_ids[0].id,
                    "product_packaging_qty": 2,
                    "product_uom": self.env.ref("uom.product_uom_kgm").id,
                    "product_uom_qty": 0.2,
                },
            ],
        )

    def test_manual_mo_cooked_sandwich(self):
        """Create a manufacturing order for a cooked sandwich, interactively."""
        sandwich = self.create_sandwich(cooked=True)
        # Create a manufacturing order
        mo_f = Form(self.env["mrp.production"])
        mo_f.product_id = sandwich
        self.assertEqual(mo_f.bom_id, sandwich.bom_ids)
        mo_f.product_qty = 10
        mo = mo_f.save()
        # Check the created manufacturing order
        self.assertEqual(mo.state, "draft")
        self.assertEqual(mo.qty_producing, 0)
        self.assertEqual(mo.product_qty, 10)
        self.assertEqual(mo.bom_id, sandwich.bom_ids)
        self.assertRecordValues(
            mo.move_raw_ids,
            [
                {
                    "bom_line_id": sandwich.bom_ids[0].bom_line_ids[0].id,
                    "product_id": self.tomato_product.id,
                    "product_packaging_id": self.tomato_product.packaging_ids[2].id,
                    "product_packaging_qty": 2.0,
                    "product_uom": self.env.ref("uom.product_uom_kgm").id,
                    "product_uom_qty": 0.1,
                },
                {
                    "bom_line_id": sandwich.bom_ids[0].bom_line_ids[1].id,
                    "product_id": self.lettuce_product.id,
                    "product_packaging_id": self.lettuce_product.packaging_ids[0].id,
                    "product_packaging_qty": 4.0,
                    "product_uom": self.env.ref("uom.product_uom_kgm").id,
                    "product_uom_qty": 0.2,
                },
                {
                    "bom_line_id": sandwich.bom_ids[0].bom_line_ids[2].id,
                    "product_id": self.bread_product.id,
                    "product_packaging_id": self.bread_product.packaging_ids[0].id,
                    "product_packaging_qty": 2,
                    "product_uom": self.env.ref("uom.product_uom_kgm").id,
                    "product_uom_qty": 0.2,
                },
            ],
        )
