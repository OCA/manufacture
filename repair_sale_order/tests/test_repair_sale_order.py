# Copyright 2022 ForgeFlow S.L. (https://forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestRepairSaleOrder(TransactionCase):
    def setUp(self):
        super(TestRepairSaleOrder, self).setUp()

        self.repair_type = self.env["repair.type"].create(
            {
                "name":  "Desk leg spare order",
                "create_sale_order": True,
            }
        )

        self.product1 = self.env["product.product"].create(
            {
                "name": "Test product",
                "standard_price": 10,
                "list_price": 20,
            }
        )

        self.product2 = self.env["product.product"].create(
            {
                "name": "Test product 2",
                "standard_price": 5,
                "list_price": 15,
            }
        )

        self.partner = self.env['res.partner'].create({
            'name': 'partner_a',
            'company_id': False,
        })

        self.repair_r1 = self.env["repair.order"].create(
            {
                "name": "Test",
                "product_id": self.product1.id,
                "partner_id": self.partner.id,
                "location_id": self.env.ref("stock.stock_location_14").id,
                "repair_type_id": self.repair_type.id,
            }
        )

        self.line = self.env["repair.line"].create(
            {
                "name": self.product2.name,
                "repair_id": self.repair_r1.id,
                "price_unit": 2.0,
                "product_id": self.product2.id,
                "product_uom_qty": 1.0,
                "location_id": self.env.ref("stock.stock_location_14").id,
                "location_dest_id": self.env.ref(
                    "product.product_product_3"
                ).property_stock_production.id,
                "company_id": self.env.company.id,
            }
        )

        self.repair_r1.operations |= self.line




    def test_repair_sale_order(self):
        self.repair_r1.action_validate()
        action = self.repair_r1.action_create_sale_order()
        self.sale_order = self.env['sale.order'].browse(action['res_id'])
        self.sale_order.action_confirm()
        self.move = self.sale_order._create_invoices()
        self.move.action_post()
