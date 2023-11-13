# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common


class TestProductionByProductCostShare(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.MrpBom = self.env["mrp.bom"]
        self.warehouse = self.env.ref("stock.warehouse0")
        route_manufacture = self.warehouse.manufacture_pull_id.route_id.id
        route_mto = self.warehouse.mto_pull_id.route_id.id
        self.uom_unit_id = self.env.ref("uom.product_uom_unit").id

        def create_product(
            name,
            standard_price,
            route_ids,
        ):
            return self.env["product.product"].create(
                {
                    "name": name,
                    "type": "product",
                    "route_ids": route_ids,
                    "standard_price": standard_price,
                }
            )

        # Products.
        self.product_a = create_product(
            "Product A", 0, [(6, 0, [route_manufacture, route_mto])]
        )
        self.product_b = create_product(
            "Product B", 0, [(6, 0, [route_manufacture, route_mto])]
        )
        self.product_c_id = create_product("Product C", 100, []).id
        self.bom_byproduct = self.MrpBom.create(
            {
                "product_tmpl_id": self.product_a.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "product_uom_id": self.uom_unit_id,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_c_id,
                            "product_uom_id": self.uom_unit_id,
                            "product_qty": 1,
                        },
                    )
                ],
                "byproduct_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_b.id,
                            "product_uom_id": self.uom_unit_id,
                            "product_qty": 1,
                            "cost_share": 15,
                        },
                    )
                ],
            }
        )

    def test_01_compute_byproduct_price(self):
        """Test BoM cost when byproducts with cost share"""
        self.assertEqual(
            self.product_a.standard_price, 0, "Initial price of the Product should be 0"
        )
        self.assertEqual(
            self.product_b.standard_price,
            0,
            "Initial price of the By-Product should be 0",
        )
        self.product_a.button_bom_cost()
        self.assertEqual(
            self.product_a.standard_price,
            85,
            "After computing price from BoM price should be 85",
        )
        self.product_b.button_bom_cost()
        self.assertEqual(
            self.product_b.standard_price,
            15,
            "After computing price from BoM price should be 15",
        )
