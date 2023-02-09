# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestMrpSaleInfo(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test mrp_sale_info product",
                "type": "product",
                "route_ids": [
                    (4, cls.env.ref("mrp.route_warehouse0_manufacture").id),
                    (4, cls.env.ref("stock.route_warehouse0_mto").id),
                ],
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Test mrp_sale_info Material", "type": "consu"}
        )
        cls.bom = cls.env["mrp.bom"].create(
            {"product_tmpl_id": cls.product.product_tmpl_id.id}
        )
        cls.env["mrp.bom.line"].create(
            {"bom_id": cls.bom.id, "product_id": cls.product_2.id, "product_qty": 2}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test client"})
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

    def test_mrp_sale_info(self):
        prev_productions = self.env["mrp.production"].search([])
        self.sale_order.action_confirm()
        production = self.env["mrp.production"].search([]) - prev_productions
        self.assertEqual(production.sale_id, self.sale_order)
        self.assertEqual(production.partner_id, self.partner)
