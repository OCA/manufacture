# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import exceptions
from odoo.tests.common import Form, TransactionCase


class TestStockReplenishmentMrpBomSelection(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Product with bill of materials
        cls.product = cls._create_product_template(cls, "Test product")
        cls.product_c1 = cls._create_product_template(cls, "Test c1")
        cls.product_c2 = cls._create_product_template(cls, "Test c2")
        cls.product_c3 = cls._create_product_template(cls, "Test c3")
        cls.product_c4 = cls._create_product_template(cls, "Test c4")
        cls.mrp_bom_1 = cls._create_mrp_bom(cls, cls.product_c1, cls.product_c2)
        cls.mrp_bom_2 = cls._create_mrp_bom(cls, cls.product_c3, cls.product_c4)
        cls.manufacturing_route_id = cls.env.ref("mrp.route_warehouse0_manufacture")

    def _create_product_template(self, name):
        product_form = Form(self.env["product.template"])
        product_form.name = name
        product_form.detailed_type = "product"
        return product_form.save()

    def _create_mrp_bom(self, component1, component2):
        mrp_bom_form = Form(self.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = self.product
        with mrp_bom_form.bom_line_ids.new() as line_form:
            line_form.product_id = component1.product_variant_ids[0]
        with mrp_bom_form.bom_line_ids.new() as line_form:
            line_form.product_id = component2.product_variant_ids[0]
        return mrp_bom_form.save()

    def test_stock_replenishment_mrp_bom_selection(self):
        orderpoint_form = Form(
            self.env["stock.warehouse.orderpoint"],
            view="stock.view_warehouse_orderpoint_tree_editable",
        )
        orderpoint_form.product_id = self.product.product_variant_ids[0]
        orderpoint_form.qty_to_order = 500
        order = orderpoint_form.save()
        # If no route is set it will not open the wizard
        with self.assertRaises(exceptions.RedirectWarning):
            order.action_replenish()
        # If the defined route is manufacturing it will open the wizard.
        order.route_id = self.manufacturing_route_id
        # Make sure that the qty is not recomputed
        order.qty_to_order = 500
        action = order.action_replenish()
        wizard = self.env[action["res_model"]].browse(action["res_id"])
        self.assertEqual(wizard.orderpoint_id, order)
        self.assertEqual(len(wizard.product_id.bom_ids), 2)
        self.assertEqual(wizard.qty_to_order, 500)
        # Have 100 produced with each production list, finally there should be 300 left
        # to be produced.
        wizard.bom_line_ids[0].qty_to_produce = 100
        wizard.bom_line_ids[1].qty_to_produce = 100
        wizard.action_confirm()
        self.assertEqual(order.qty_to_order, 300)
        # Check that 2 production orders have been created.
        mrp_production_orders = self.env["mrp.production"].search(
            [("product_id", "=", self.product.product_variant_ids[0].id)]
        )
        self.assertEqual(len(mrp_production_orders), 2)
        # Check that all the products have been added to the production orders.
        mrp_bom_1_product_ids = self.mrp_bom_1.bom_line_ids.product_id.ids
        mrp_bom_2_product_ids = self.mrp_bom_2.bom_line_ids.product_id.ids
        production_product_ids = mrp_production_orders.move_raw_ids.product_id.ids
        for product_id in mrp_bom_1_product_ids:
            self.assertIn(product_id, production_product_ids)
        for product_id in mrp_bom_2_product_ids:
            self.assertIn(product_id, production_product_ids)
