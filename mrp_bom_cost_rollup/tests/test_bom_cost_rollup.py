# Copyright 2026 Cubiczan
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestBomCostRollup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Product = cls.env["product.product"]
        cls.Bom = cls.env["mrp.bom"]

        # Components with a known cost.
        cls.screw = cls.Product.create(
            {
                "name": "Screw",
                "type": "consu",
                "is_storable": True,
                "standard_price": 0.50,
            }
        )
        cls.plank = cls.Product.create(
            {
                "name": "Plank",
                "type": "consu",
                "is_storable": True,
                "standard_price": 8.00,
            }
        )
        # Finished product.
        cls.table = cls.Product.create(
            {
                "name": "Table",
                "type": "consu",
                "is_storable": True,
                "standard_price": 0.0,
            }
        )

    def _make_bom(self, product, qty, lines):
        return self.Bom.create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_id": product.id,
                "product_qty": qty,
                "type": "normal",
                "bom_line_ids": [
                    (0, 0, {"product_id": comp.id, "product_qty": comp_qty})
                    for comp, comp_qty in lines
                ],
            }
        )

    def test_components_rollup(self):
        # Table = 4 planks (8.00) + 16 screws (0.50) = 32 + 8 = 40.00 for 1 unit.
        bom = self._make_bom(self.table, 1, [(self.plank, 4), (self.screw, 16)])
        self.assertAlmostEqual(bom.bom_cost, 40.0)
        self.assertAlmostEqual(bom.bom_unit_cost, 40.0)

    def test_batch_unit_cost(self):
        # Define the BoM to produce 2 tables; unit cost must divide out.
        bom = self._make_bom(self.table, 2, [(self.plank, 8), (self.screw, 32)])
        self.assertAlmostEqual(bom.bom_cost, 80.0)
        self.assertAlmostEqual(bom.bom_unit_cost, 40.0)

    def test_nested_bom_rollup(self):
        # A leg is itself manufactured: 1 plank = 8.00; a table uses 4 legs + 16 screws.
        leg = self.Product.create(
            {"name": "Leg", "type": "consu", "is_storable": True, "standard_price": 0.0}
        )
        self._make_bom(leg, 1, [(self.plank, 1)])
        table_bom = self._make_bom(self.table, 1, [(leg, 4), (self.screw, 16)])
        # 4 legs * 8.00 + 16 screws * 0.50 = 32 + 8 = 40.00
        self.assertAlmostEqual(table_bom.bom_cost, 40.0)

    def test_set_standard_price_from_bom(self):
        bom = self._make_bom(self.table, 1, [(self.plank, 4), (self.screw, 16)])
        bom.action_set_standard_price_from_bom()
        self.assertAlmostEqual(self.table.standard_price, 40.0)
