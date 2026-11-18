# Copyright 2026 Dixmit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import Command
from odoo.tests import TransactionCase


class TestFixedQty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        uom_unit = cls.env.ref("uom.product_uom_unit")
        uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.finished = cls.env["product.product"].create(
            {
                "name": "Packed",
                "uom_id": uom_unit.id,
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.bulk = cls.env["product.product"].create(
            {"name": "Bulk", "uom_id": uom_kg.id, "type": "consu", "is_storable": True}
        )
        cls.label = cls.env["product.product"].create(
            {
                "name": "Label",
                "uom_id": uom_unit.id,
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.box = cls.env["product.product"].create(
            {"name": "Box", "uom_id": uom_unit.id, "type": "consu", "is_storable": True}
        )
        cls.sample = cls.env["product.product"].create(
            {
                "name": "Sample",
                "uom_id": uom_unit.id,
                "type": "consu",
                "is_storable": True,
            }
        )
        # BoM: 1 kg of bulk gives 6 packed units
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.finished.product_tmpl_id.id,
                "product_qty": 6,
                "product_uom_id": uom_unit.id,
                "bom_line_ids": [
                    # Proportional + fixed: 1 kg per 6 units, plus 0.5 kg per order
                    Command.create(
                        {
                            "product_id": cls.bulk.id,
                            "product_qty": 1,
                            "product_uom_id": uom_kg.id,
                            "fixed_qty": 0.5,
                        }
                    ),
                    # Proportional only: 6 labels per 6 units
                    Command.create(
                        {
                            "product_id": cls.label.id,
                            "product_qty": 6,
                            "product_uom_id": uom_unit.id,
                        }
                    ),
                    # Fixed only: one box per order whatever the size
                    Command.create(
                        {
                            "product_id": cls.box.id,
                            "product_qty": 0,
                            "product_uom_id": uom_unit.id,
                            "fixed_qty": 1,
                        }
                    ),
                ],
                "byproduct_ids": [
                    # Fixed only: one sample per order, no cost
                    Command.create(
                        {
                            "product_id": cls.sample.id,
                            "product_qty": 0,
                            "product_uom_id": uom_unit.id,
                            "fixed_qty": 1,
                            "cost_share": 0,
                        }
                    ),
                ],
            }
        )

    def _create_mo(self, qty):
        return self.env["mrp.production"].create(
            {
                "product_id": self.finished.id,
                "bom_id": self.bom.id,
                "product_qty": qty,
                "product_uom_id": self.finished.uom_id.id,
            }
        )

    def _raw_qty(self, mo, product):
        move = mo.move_raw_ids.filtered(lambda m: m.product_id == product)
        self.assertEqual(len(move), 1, f"Expected one raw move for {product.name}")
        return move.product_uom_qty

    def _finished_move(self, mo, product):
        move = mo.move_finished_ids.filtered(lambda m: m.product_id == product)
        self.assertEqual(len(move), 1, f"Expected one finished move for {product.name}")
        return move

    def test_default_is_zero(self):
        line = self.bom.bom_line_ids.filtered(lambda r: r.product_id == self.label)
        self.assertEqual(line.fixed_qty, 0.0)

    def test_component_proportional_plus_fixed(self):
        """60 units -> 10 kg proportional + 0.5 kg fixed."""
        mo = self._create_mo(60)
        self.assertAlmostEqual(self._raw_qty(mo, self.bulk), 10.5)

    def test_component_without_fixed_is_unchanged(self):
        mo = self._create_mo(60)
        self.assertAlmostEqual(self._raw_qty(mo, self.label), 60)

    def test_component_fixed_only(self):
        """A line with zero proportional qty is always the fixed quantity."""
        for qty in (6, 60, 600):
            mo = self._create_mo(qty)
            self.assertAlmostEqual(self._raw_qty(mo, self.box), 1)

    def test_fixed_part_does_not_scale(self):
        """Halving the order halves the proportional part only."""
        mo = self._create_mo(60)
        mo.product_qty = 30
        self.assertAlmostEqual(self._raw_qty(mo, self.bulk), 5.5)
        self.assertAlmostEqual(self._raw_qty(mo, self.label), 30)
        self.assertAlmostEqual(self._raw_qty(mo, self.box), 1)

    def test_byproduct_fixed_qty(self):
        for qty in (6, 60, 600):
            mo = self._create_mo(qty)
            self.assertAlmostEqual(
                self._finished_move(mo, self.sample).product_uom_qty, 1
            )

    def test_main_product_quantity_is_not_affected(self):
        mo = self._create_mo(60)
        self.assertAlmostEqual(
            self._finished_move(mo, self.finished).product_uom_qty, 60
        )

    def test_byproduct_cost_share_is_zero(self):
        """The main product keeps 100% of the cost."""
        mo = self._create_mo(60)
        self.assertEqual(self._finished_move(mo, self.sample).cost_share, 0)
        self.assertEqual(self._finished_move(mo, self.finished).cost_share, 0)
        self.assertEqual(sum(mo.move_byproduct_ids.mapped("cost_share")), 0)

    def test_confirm_keeps_quantities_(self):
        mo = self._create_mo(60)
        mo.action_confirm()
        self.assertAlmostEqual(self._raw_qty(mo, self.bulk), 10.5)
        self.assertAlmostEqual(self._finished_move(mo, self.sample).product_uom_qty, 1)
        mo = self._create_mo(600)
        mo.action_confirm()
        self.assertAlmostEqual(self._raw_qty(mo, self.bulk), 100.5)
        self.assertAlmostEqual(self._finished_move(mo, self.sample).product_uom_qty, 1)
