# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import RecordCapturer, common


class TestMrpSaleInfo(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        warehouse = cls.env.ref("stock.warehouse0")
        warehouse.write(
            {"delivery_steps": "pick_pack_ship", "manufacture_steps": "pbm_sam"}
        )
        route_manufacture_1 = cls.env.ref("mrp.route_warehouse0_manufacture")
        route_manufacture_2 = cls.env.ref("stock.route_warehouse0_mto")
        route_manufacture_2.active = True
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test mrp_sale_info product",
                "type": "product",
                "route_ids": [
                    (4, route_manufacture_1.id),
                    (4, route_manufacture_2.id),
                ],
            }
        )
        cls.product_kit = cls.env["product.product"].create(
            {
                "name": "Test kit",
                "type": "product",
                "route_ids": [
                    (4, route_manufacture_1.id),
                    (4, route_manufacture_2.id),
                ],
            }
        )
        cls.product_kit_comp = cls.env["product.product"].create(
            {
                "name": "Test kit comp",
                "type": "product",
                "route_ids": [
                    (4, route_manufacture_1.id),
                    (4, route_manufacture_2.id),
                ],
            }
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "operation_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test operation",
                            "workcenter_id": cls.env.ref("mrp.mrp_workcenter_3").id,
                        },
                    )
                ],
            }
        )
        cls.bom_kit = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_kit.product_tmpl_id.id,
                "type": "phantom",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_kit_comp.id,
                        },
                    ),
                ],
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test client"})
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "client_order_ref": "SO1",
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

    def test_mrp_sale_info(self):
        with RecordCapturer(self.env["mrp.production"], []) as capture:
            self.sale_order.action_confirm()
        production = capture.records
        self.assertEqual(production.sale_id, self.sale_order)
        self.assertEqual(production.partner_id, self.partner)
        self.assertEqual(production.client_order_ref, self.sale_order.client_order_ref)
        self.assertEqual(self.sale_order.order_line.created_production_ids, production)

    def test_mrp_workorder(self):
        with RecordCapturer(self.env["mrp.workorder"], []) as capture:
            self.sale_order.action_confirm()
        workorder = capture.records
        self.assertEqual(workorder.sale_id, self.sale_order)
        self.assertEqual(workorder.partner_id, self.partner)
        self.assertEqual(workorder.client_order_ref, self.sale_order.client_order_ref)

    def test_kit(self):
        self.sale_order.write(
            {
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_kit.id,
                            "product_uom_qty": 2,
                            "price_unit": 1,
                        },
                    )
                ]
            }
        )
        with RecordCapturer(self.env["mrp.production"], []) as capture:
            self.sale_order.action_confirm()
        productions = capture.records
        for order_line in self.sale_order.order_line:
            for created_prod in order_line.created_production_ids:
                self.assertIn(created_prod, productions)
                self.assertEqual(created_prod.product_qty, order_line.product_uom_qty)
