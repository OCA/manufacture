# Copyright 2025 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from types import SimpleNamespace
from unittest.mock import patch

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.mrp.models.stock_rule import StockRule as MrpStockRule


class TestMrpBomFind(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_mrp_bom_assign_auto=True,
                tracking_disable=True,
            )
        )
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
        cls.product_d = Product.create(
            {
                "name": "Product D",
                "type": "consu",
                "is_storable": True,
                "standard_price": 5,
            }
        )
        cls.product_e = Product.create(
            {
                "name": "Product E",
                "type": "consu",
                "is_storable": True,
                "standard_price": 5,
            }
        )
        cls.product_no_bom = Product.create(
            {
                "name": "Product Without BOM",
                "type": "consu",
                "is_storable": True,
                "standard_price": 5,
            }
        )
        cls.product_service = Product.create(
            {
                "name": "Service Component",
                "type": "service",
                "standard_price": 5,
            }
        )
        cls.product_zero = Product.create(
            {
                "name": "Zero Quantity Component",
                "type": "consu",
                "is_storable": True,
                "standard_price": 5,
            }
        )
        cls.product_f = Product.create(
            {
                "name": "Product F",
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
        cls.bom_multi_line = Bom.create(
            {
                "product_tmpl_id": cls.product_a.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "sequence": -1,
            }
        )
        cls.bom_d = Bom.create(
            {
                "product_tmpl_id": cls.product_d.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )
        cls.bom_d_alternative = Bom.create(
            {
                "product_tmpl_id": cls.product_d.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )
        cls.bom_d_kit = Bom.create(
            {
                "product_tmpl_id": cls.product_d.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "phantom",
            }
        )
        cls.bom_d_kit_alternative = Bom.create(
            {
                "product_tmpl_id": cls.product_d.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "phantom",
            }
        )
        cls.bom_product = Bom.create(
            {
                "product_tmpl_id": cls.product_f.product_tmpl_id.id,
                "product_id": cls.product_f.id,
                "product_qty": 1.0,
                "type": "normal",
                "sequence": 99,
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
        BomLine.create(
            {
                "bom_id": cls.bom_multi_line.id,
                "product_id": cls.product_b.id,
                "product_qty": 5.0,
            }
        )
        BomLine.create(
            {
                "bom_id": cls.bom_multi_line.id,
                "product_id": cls.product_c.id,
                "product_qty": 5.0,
            }
        )
        BomLine.create(
            {
                "bom_id": cls.bom_d.id,
                "product_id": cls.product_b.id,
                "product_qty": 6.0,
            }
        )
        BomLine.create(
            {
                "bom_id": cls.bom_d_alternative.id,
                "product_id": cls.product_e.id,
                "product_qty": 1.0,
            }
        )
        BomLine.create(
            {
                "bom_id": cls.bom_d_kit.id,
                "product_id": cls.product_b.id,
                "product_qty": 6.0,
            }
        )
        BomLine.create(
            {
                "bom_id": cls.bom_d_kit_alternative.id,
                "product_id": cls.product_e.id,
                "product_qty": 1.0,
            }
        )
        BomLine.create(
            {
                "bom_id": cls.bom_product.id,
                "product_id": cls.product_service.id,
                "product_qty": 1.0,
            }
        )
        BomLine.create(
            {
                "bom_id": cls.bom_product.id,
                "product_id": cls.product_zero.id,
                "product_qty": 0.0,
            }
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.child_location = cls.env["stock.location"].create(
            {
                "name": "Alternative Stock",
                "location_id": cls.stock_location.id,
                "usage": "internal",
                "company_id": cls.env.company.id,
            }
        )
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
        Quant.create(
            {
                "product_id": cls.product_e.id,
                "location_id": cls.stock_location.id,
                "quantity": 10.0,
            }
        )
        Quant.create(
            {
                "product_id": cls.product_e.id,
                "location_id": cls.child_location.id,
                "quantity": 5.0,
            }
        )

    def test_bom_find_with_sufficient_stock(self):
        res = self.env["mrp.bom"]._bom_find(self.product_a)
        self.assertIn(self.product_a, res.keys())
        self.assertEqual(res[self.product_a], self.bom_a)

    def test_bom_find_with_insufficient_stock(self):
        # Change stock so it has to take second BoM
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

    def test_bom_find_per_product(self):
        res = self.env["mrp.bom"]._bom_find(
            self.product_a | self.product_d | self.product_f
        )
        self.assertEqual(res[self.product_a], self.bom_a)
        self.assertEqual(res[self.product_d], self.bom_d)
        self.assertEqual(res[self.product_f], self.bom_product)

    def test_bom_find_with_demand_quantity(self):
        res = (
            self.env["mrp.bom"]
            .with_context(mrp_bom_assign_auto_quantities={self.product_d.id: 2.0})
            ._bom_find(self.product_d)
        )
        self.assertEqual(res[self.product_d], self.bom_d_alternative)

    def test_bom_find_with_location(self):
        res = (
            self.env["mrp.bom"]
            .with_context(location=self.child_location.id)
            ._bom_find(self.product_d)
        )
        self.assertEqual(res[self.product_d], self.bom_d_alternative)

    def test_bom_find_phantom_with_location(self):
        res = (
            self.env["mrp.bom"]
            .with_context(location=self.child_location.id)
            ._bom_find(self.product_d, bom_type="phantom")
        )
        self.assertEqual(res[self.product_d], self.bom_d_kit_alternative)

    def test_bom_is_available_skips_service_and_zero_quantity(self):
        self.assertTrue(
            self.env["mrp.bom"]._bom_is_available(self.bom_product, self.product_f, {})
        )

    def test_bom_find_falls_back_to_standard(self):
        res = self.env["mrp.bom"]._bom_find(self.product_no_bom)
        self.assertFalse(res[self.product_no_bom])

        res = self.env["mrp.bom"]._bom_find(self.product_a | self.product_no_bom)
        self.assertEqual(res[self.product_a], self.bom_a)
        self.assertFalse(res[self.product_no_bom])

    def test_bom_find_with_invalid_stock_check(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "mrp_bom_assign_auto.bom_stock_check", "invalid"
        )
        res = self.env["mrp.bom"]._bom_find(self.product_a)
        self.assertEqual(res[self.product_a], self.bom_a)

    def test_bom_find_with_location_context_map(self):
        res = (
            self.env["mrp.bom"]
            .with_context(
                mrp_bom_assign_auto_locations={
                    self.product_d.id: self.child_location.id,
                }
            )
            ._bom_find(self.product_d)
        )
        self.assertEqual(res[self.product_d], self.bom_d_alternative)

    def test_bom_find_with_picking_type_location(self):
        picking_type = self.env["stock.picking.type"].search(
            [("default_location_src_id", "=", self.stock_location.id)], limit=1
        )
        self.assertTrue(picking_type)
        res = self.env["mrp.bom"]._bom_find(self.product_d, picking_type=picking_type)
        self.assertEqual(res[self.product_d], self.bom_d)

    def test_get_demand_quantity_with_invalid_context(self):
        demand = (
            self.env["mrp.bom"]
            .with_context(mrp_bom_assign_auto_quantities=[])
            ._get_demand_quantity(self.product_d)
        )
        self.assertIsNone(demand)

    def test_compute_bom_without_product(self):
        production = self.env["mrp.production"].new(
            {"product_qty": 1.0, "company_id": self.env.company.id}
        )
        production._compute_bom_id()
        self.assertFalse(production.bom_id)

    def test_stock_rule_propagates_procurement_context(self):
        warehouse = self.env["stock.warehouse"].search([], limit=1)
        procurement = SimpleNamespace(
            company_id=warehouse.company_id,
            product_uom=self.product_d.uom_id,
            product_qty=2.0,
            product_id=self.product_d,
            values={"warehouse_id": warehouse.id},
        )
        skipped_procurement = SimpleNamespace(
            company_id=warehouse.company_id,
            product_uom=self.product_d.uom_id,
            product_qty=0.0,
            product_id=self.product_d,
            values={},
        )
        captured = {}

        def fake_run(stock_rule, procurements, raise_user_error=True):
            captured["context"] = stock_rule.env.context
            captured["procurements"] = procurements
            captured["raise_user_error"] = raise_user_error
            return "result"

        with patch.object(MrpStockRule, "run", new=fake_run):
            result = self.env["stock.rule"].run(
                [skipped_procurement, procurement], raise_user_error=False
            )

        self.assertEqual(result, "result")
        self.assertEqual(
            captured["context"]["mrp_bom_assign_auto_quantities"],
            {self.product_d.id: 2.0},
        )
        self.assertEqual(
            captured["context"]["mrp_bom_assign_auto_locations"],
            {self.product_d.id: warehouse.lot_stock_id.id},
        )
        self.assertEqual(captured["procurements"], [skipped_procurement, procurement])
        self.assertFalse(captured["raise_user_error"])
