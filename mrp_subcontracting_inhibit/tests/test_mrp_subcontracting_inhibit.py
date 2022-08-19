# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form, common


class TestMrpSubcontractingInhibit(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.subcontractor_mto_route = cls.env.ref(
            "mrp_subcontracting.route_resupply_subcontractor_mto"
        )
        cls.subcontractor_mto_route.subcontracting_inhibit = True
        cls.buy_route = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.supplier = cls.env["res.partner"].create({"name": "Mr Odoo"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "product",
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": cls.supplier.id,
                            "min_qty": 1,
                            "price": 5,
                            "subcontracting_inhibit": True,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.supplier.id,
                            "min_qty": 1,
                            "price": 10,
                        },
                    ),
                ],
            }
        )
        cls.component = cls.env["product.product"].create(
            {
                "name": "Test Component",
                "route_ids": [(6, 0, [cls.subcontractor_mto_route.id])],
            }
        )
        cls.bom = cls._create_mrp_bom(cls)

    def _create_mrp_bom(self):
        mrp_bom_form = Form(self.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = self.product.product_tmpl_id
        mrp_bom_form.type = "subcontract"
        mrp_bom_form.subcontractor_ids.add(self.supplier)
        with mrp_bom_form.bom_line_ids.new() as line_form:
            line_form.product_id = self.component
            line_form.product_qty = 1
        return mrp_bom_form.save()

    def _product_replenish(self, product, qty, route_id):
        replenish_form = Form(
            self.env["product.replenish"].with_context(default_product_id=product.id)
        )
        replenish_form.quantity = qty
        replenish_form.route_ids.add(route_id)
        replenish = replenish_form.save()
        replenish.launch_replenishment()

    def _get_purchase_order(self):
        return self.env["purchase.order"].search(
            [("partner_id", "=", self.supplier.id)]
        )

    def _get_mrp_production_total(self):
        return self.env["mrp.production"].search_count([("bom_id", "=", self.bom.id)])

    def test_misc_buy_route(self):
        # Check if the value is correct
        self._product_replenish(self.product, 1, self.buy_route)
        order = self._get_purchase_order()
        self.assertFalse(order.order_line.subcontracting_inhibit)
        # Check if price is correct
        self.assertEqual(order.order_line.price_unit, 10)
        order.order_line.product_qty = 2
        order.order_line._onchange_quantity()
        self.assertEqual(order.order_line.price_unit, 10)
        order.button_confirm()
        self.assertEqual(self._get_mrp_production_total(), 1)

    def test_misc_buy_subcontractor_route(self):
        # Check if the value is correct
        self._product_replenish(self.product, 1, self.subcontractor_mto_route)
        order = self._get_purchase_order()
        self.assertTrue(order.order_line.subcontracting_inhibit)
        # Check if price is correct
        self.assertEqual(order.order_line.price_unit, 5)
        order.order_line.product_qty = 2
        order.order_line._onchange_quantity()
        self.assertEqual(order.order_line.price_unit, 5)
        order.button_confirm()
        self.assertEqual(self._get_mrp_production_total(), 0)
