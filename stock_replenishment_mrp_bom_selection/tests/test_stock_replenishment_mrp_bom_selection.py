# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import exceptions
from odoo.tests import Form, TransactionCase


class TestStockReplenishmentMrpBomSelection(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Product with bill of materials
        cls.product = cls._create_product_template("Test product")
        cls.product_c1 = cls._create_product_template("Test c1")
        cls.product_c2 = cls._create_product_template("Test c2")
        cls.product_c3 = cls._create_product_template("Test c3")
        cls.product_c4 = cls._create_product_template("Test c4")
        cls.mrp_bom_1 = cls._create_mrp_bom(cls.product_c1, cls.product_c2)
        cls.mrp_bom_2 = cls._create_mrp_bom(cls.product_c3, cls.product_c4)
        cls.manufacturing_route = cls.env.ref("mrp.route_warehouse0_manufacture")

    @classmethod
    def _create_product_template(cls, name):
        product_form = Form(cls.env["product.template"])
        product_form.name = name
        product_form.is_storable = True
        return product_form.save()

    @classmethod
    def _create_mrp_bom(cls, component1, component2):
        mrp_bom_form = Form(cls.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = cls.product
        with mrp_bom_form.bom_line_ids.new() as line_form:
            line_form.product_id = component1.product_variant_ids[0]
        with mrp_bom_form.bom_line_ids.new() as line_form:
            line_form.product_id = component2.product_variant_ids[0]
        return mrp_bom_form.save()

    def _create_orderpoint(self, product):
        orderpoint_form = Form(
            self.env["stock.warehouse.orderpoint"],
            view="stock.view_warehouse_orderpoint_tree_editable",
        )
        orderpoint_form.product_id = product
        # `qty_to_order` is only editable on manually triggered orderpoints
        orderpoint_form.trigger = "manual"
        orderpoint_form.qty_to_order = 500
        return orderpoint_form.save()

    def test_no_bom_no_wizard(self):
        """A product without BoM keeps the standard behavior."""
        product = self._create_product_template("Test without BoM")
        orderpoint = self._create_orderpoint(product.product_variant_ids[0])
        self.assertFalse(orderpoint.show_bom)
        with self.assertRaises(exceptions.RedirectWarning):
            orderpoint.action_replenish()

    def test_auto_trigger_no_wizard(self):
        """Automatic orderpoints keep the standard behavior."""
        orderpoint = self._create_orderpoint(self.product.product_variant_ids[0])
        orderpoint.route_id = self.manufacturing_route
        orderpoint.product_max_qty = 10
        orderpoint.trigger = "auto"
        self.assertTrue(orderpoint.show_bom)
        action = orderpoint.action_replenish()
        self.assertNotEqual(
            (action or {}).get("res_model"),
            "stock.warehouse.orderpoint.replenish.wizard",
        )
        self.assertTrue(
            self.env["mrp.production"].search_count(
                [("product_id", "=", self.product.product_variant_ids[0].id)]
            )
        )

    def test_stock_replenishment_mrp_bom_selection(self):
        orderpoint = self._create_orderpoint(self.product.product_variant_ids[0])
        # The manufacturing route makes the wizard show up
        orderpoint.route_id = self.manufacturing_route
        # Make sure that the qty is not recomputed
        orderpoint.qty_to_order = 500
        action = orderpoint.action_replenish()
        wizard = self.env[action["res_model"]].browse(action["res_id"])
        self.assertEqual(wizard.orderpoint_id, orderpoint)
        self.assertEqual(len(wizard.bom_line_ids), 2)
        self.assertEqual(wizard.bom_line_ids.bom_id, self.mrp_bom_1 | self.mrp_bom_2)
        self.assertEqual(wizard.qty_to_order, 500)
        # Nothing filled in means nothing to do
        with self.assertRaises(exceptions.UserError):
            wizard.action_confirm()
        # More than the quantity to order is not allowed either
        wizard.bom_line_ids[0].qty_to_produce = 600
        with self.assertRaises(exceptions.UserError):
            wizard.action_confirm()
        # Have 100 produced with each production list, finally there should be 300 left
        # to be produced.
        wizard.bom_line_ids[0].qty_to_produce = 100
        wizard.bom_line_ids[1].qty_to_produce = 100
        self.assertEqual(wizard.total_qty_to_produce, 200)
        self.assertEqual(wizard.qty_remaining_to_produce, 300)
        # Emulate a fresh RPC call, so that `qty_remaining_to_produce` is computed
        # from scratch inside `action_confirm()` and not read from the cache.
        self.env.invalidate_all()
        wizard.action_confirm()
        self.assertEqual(orderpoint.qty_to_order, 300)
        # The BoM selection is not kept on the orderpoint
        self.assertFalse(orderpoint.bom_id)
        # Check that 2 production orders have been created, one per BoM.
        mrp_production_orders = self.env["mrp.production"].search(
            [("product_id", "=", self.product.product_variant_ids[0].id)]
        )
        self.assertEqual(len(mrp_production_orders), 2)
        self.assertEqual(mrp_production_orders.bom_id, self.mrp_bom_1 | self.mrp_bom_2)
        for production in mrp_production_orders:
            self.assertEqual(production.product_qty, 100)
        # Check that all the products have been added to the production orders.
        mrp_bom_1_product_ids = self.mrp_bom_1.bom_line_ids.product_id.ids
        mrp_bom_2_product_ids = self.mrp_bom_2.bom_line_ids.product_id.ids
        production_product_ids = mrp_production_orders.move_raw_ids.product_id.ids
        for product_id in mrp_bom_1_product_ids:
            self.assertIn(product_id, production_product_ids)
        for product_id in mrp_bom_2_product_ids:
            self.assertIn(product_id, production_product_ids)

    def test_material_availability_wizard(self):
        component = self.mrp_bom_1.bom_line_ids[0].product_id
        self.env["stock.quant"]._update_available_quantity(
            component, self.env.ref("stock.stock_location_stock"), 42
        )
        orderpoint = self._create_orderpoint(self.product.product_variant_ids[0])
        orderpoint.route_id = self.manufacturing_route
        action = orderpoint.action_replenish()
        wizard = self.env[action["res_model"]].browse(action["res_id"])
        line = wizard.bom_line_ids.filtered(lambda x: x.bom_id == self.mrp_bom_1)
        # Only 42 units of one component => nothing can be produced without the other
        self.assertEqual(line.max_production_qty, 0)
        popup_action = line.action_material_availability_popup()
        popup = (
            self.env[popup_action["res_model"]]
            .with_context(**popup_action["context"])
            .create({})
        )
        self.assertEqual(len(popup.product_ids), 2)
        self.assertEqual(
            popup.product_ids.filtered(
                lambda x: x.product_id == component
            ).product_qty_available,
            42,
        )
        self.assertEqual(popup.action_close()["res_id"], wizard.id)
