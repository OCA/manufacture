# Copyright 2025 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.base.tests.common import BaseCommon


class TestMrpBomFind(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, test_mrp_bom_assign_auto=True))
        Bom = cls.env["mrp.bom"]
        BomLine = cls.env["mrp.bom.line"]
        Product = cls.env["product.product"]
        Quant = cls.env["stock.quant"]
        cls.product_a = Product.create(
            {
                "name": "Product A",
                "type": "consu",
                "is_storable": True,
                "standard_price": 10,
            }
        )
        cls.product_b = Product.create(
            {
                "name": "Product B",
                "type": "consu",
                "is_storable": True,
                "standard_price": 5,
            }
        )
        cls.product_c = Product.create(
            {
                "name": "Product B",
                "type": "consu",
                "is_storable": True,
                "standard_price": 5,
            }
        )
        cls.bom_a = Bom.create(
            {
                "product_tmpl_id": cls.product_a.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )
        cls.bom_b = Bom.create(
            {
                "product_tmpl_id": cls.product_a.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )
        BomLine.create(
            {
                "bom_id": cls.bom_a.id,
                "product_id": cls.product_b.id,
                "product_qty": 5.0,
            }
        )
        BomLine.create(
            {
                "bom_id": cls.bom_b.id,
                "product_id": cls.product_c.id,
                "product_qty": 5.0,
            }
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        Quant.create(
            {
                "product_id": cls.product_b.id,
                "location_id": cls.stock_location.id,
                "quantity": 10.0,
            }
        )
        Quant.create(
            {
                "product_id": cls.product_c.id,
                "location_id": cls.stock_location.id,
                "quantity": 2.0,
            }
        )

    def test_bom_find_with_sufficient_stock(self):
        res = self.env["mrp.bom"]._bom_find(self.product_a)
        self.assertIn(self.product_a, res.keys())
        self.assertEqual(res[self.product_a], self.bom_a)

    def test_bom_find_with_insufficient_stock(self):
        # Chnage stock so it has to take second BoM
        quant_b = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.product_b.id),
                ("location_id", "=", self.stock_location.id),
            ]
        )
        quant_c = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.product_c.id),
                ("location_id", "=", self.stock_location.id),
            ]
        )
        quant_b.write({"quantity": 2.0})
        quant_c.write({"quantity": 5.0})
        res = self.env["mrp.bom"]._bom_find(self.product_a)
        self.assertIn(self.product_a, res.keys())
        self.assertEqual(res[self.product_a], self.bom_b)
