# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.tests import Form, common


class TestStockWholeKitConstraint(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        # Kit 1 that can be partially delivered
        cls.product_kit_1 = cls.env["product.product"].create(
            {"name": "Product Kit 1", "type": "consu"}
        )
        cls.component_1_kit_1 = cls.env["product.product"].create(
            {"name": "Component 1 Kit 1", "type": "product"}
        )
        cls.component_2_kit_1 = cls.env["product.product"].create(
            {"name": "Component 2 Kit 1", "type": "product"}
        )
        bom_form = Form(cls.env["mrp.bom"])
        bom_form.product_tmpl_id = cls.product_kit_1.product_tmpl_id
        bom_form.product_id = cls.product_kit_1
        bom_form.type = "phantom"
        with bom_form.bom_line_ids.new() as line:
            line.product_id = cls.component_1_kit_1
        with bom_form.bom_line_ids.new() as line:
            line.product_id = cls.component_2_kit_1
        cls.bom_kit_1 = bom_form.save()
        # Kit 2 - disallow partial deliveries
        cls.product_kit_2 = cls.env["product.product"].create(
            {
                "name": "Product Kit 2",
                "type": "consu",
                "allow_partial_kit_delivery": False,
            }
        )
        cls.component_1_kit_2 = cls.env["product.product"].create(
            {"name": "Component 1 Kit 2", "type": "product"}
        )
        cls.component_2_kit_2 = cls.env["product.product"].create(
            {"name": "Component 2 Kit 2", "type": "product"}
        )
        bom_form = Form(cls.env["mrp.bom"])
        bom_form.product_tmpl_id = cls.product_kit_2.product_tmpl_id
        bom_form.product_id = cls.product_kit_2
        bom_form.type = "phantom"
        with bom_form.bom_line_ids.new() as line:
            line.product_id = cls.component_1_kit_2
        with bom_form.bom_line_ids.new() as line:
            line.product_id = cls.component_2_kit_2
        cls.bom_kit_2 = bom_form.save()
        # Manufactured product as control
        cls.product_mrp = cls.env["product.product"].create(
            {
                "name": "Product Kit 2",
                "type": "consu",
                # Force the setting in a manufactured product.
                # It should not affect it
                "allow_partial_kit_delivery": False,
            }
        )
        bom_form = Form(cls.env["mrp.bom"])
        bom_form.product_tmpl_id = cls.product_mrp.product_tmpl_id
        bom_form.product_id = cls.product_mrp
        bom_form.type = "normal"
        with bom_form.bom_line_ids.new() as line:
            line.product_id = cls.component_1_kit_2
        cls.bom_mrp = bom_form.save()
        # Not a kit product as control
        cls.regular_product = cls.env["product.product"].create(
            {
                "name": "Regular test product",
                "type": "product",
                # Force the setting in a regular product. It should not affect it
                "allow_partial_kit_delivery": False,
            }
        )
        # Delivery picking
        picking_form = Form(cls.env["stock.picking"])
        picking_form.picking_type_id = cls.env.ref("stock.picking_type_out")
        picking_form.partner_id = cls.customer
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = cls.product_kit_1
            move.product_uom_qty = 3.0
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = cls.product_kit_2
            move.product_uom_qty = 3.0
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = cls.product_mrp
            move.product_uom_qty = 3.0
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = cls.regular_product
            move.product_uom_qty = 3.0
        cls.customer_picking = picking_form.save()
        cls.customer_picking.action_confirm()

    def test_01_all_partially_done_but_the_disallow_partial_kit(self):
        """No quantity is done for the kit disallowed and only partially for the
        others so the backorder wizard raises."""
        moves_allowed = self.customer_picking.move_lines.filtered(
            lambda x: x.bom_line_id.bom_id != self.bom_kit_2
        )
        moves_allowed.write({"quantity_done": 1})
        response = self.customer_picking.button_validate()
        self.assertEqual("stock.backorder.confirmation", response.get("res_model"))

    def test_02_all_done_but_partial_disallow_partial_kit(self):
        """We try to deliver partially the disallowed kit"""
        moves_disallowed = self.customer_picking.move_lines.filtered(
            lambda x: x.bom_line_id.bom_id == self.bom_kit_2
        )
        moves_disallowed.write({"quantity_done": 1})
        with self.assertRaises(ValidationError):
            self.customer_picking.button_validate()
        # We can split the picking if the whole kit components are delivered
        moves_disallowed.write({"quantity_done": 3})
        # We've got a backorder on the rest of the lines
        response = self.customer_picking.button_validate()
        self.assertEqual("stock.backorder.confirmation", response.get("res_model"))

    def test_03_all_done(self):
        """Deliver the whole picking normally"""
        self.customer_picking.move_lines.write({"quantity_done": 3})
        self.customer_picking.button_validate()
        self.assertEqual("done", self.customer_picking.state)

    def test_04_manual_move_lines(self):
        """If a user adds manual operations, we should consider it as well"""
        # We need to enable detaild operations to test this case
        self.customer_picking.picking_type_id.show_operations = True
        picking_form = Form(self.customer_picking)
        for product in (self.bom_kit_1 + self.bom_kit_2).mapped(
            "bom_line_ids.product_id"
        ):
            with picking_form.move_line_ids_without_package.new() as line:
                line.product_id = product
                line.qty_done = 3
        picking_form.save()
        self.customer_picking.move_lines.filtered(
            lambda x: x.product_id in (self.product_mrp, self.regular_product)
        ).write({"quantity_done": 3})
        self.customer_picking.button_validate()
        self.assertEqual("done", self.customer_picking.state)
