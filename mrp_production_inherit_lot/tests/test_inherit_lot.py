# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestInheritLot(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.result_product = cls.env["product.product"].create(
            {"name": "Test Product", "tracking": "lot"}
        )
        cls.sub_product_01 = cls.env["product.product"].create(
            {"name": "Sub Product 01", "tracking": "lot"}
        )
        cls.sub_product_02 = cls.env["product.product"].create(
            {"name": "Sub Product 02", "tracking": "lot"}
        )
        cls.sub_product_03 = cls.env["product.product"].create(
            {"name": "Sub Product 03", "tracking": "lot"}
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.result_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "byproduct_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.sub_product_01.id,
                            "inherit_lot": True,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.sub_product_02.id,
                            "inherit_lot": True,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.sub_product_03.id,
                            "inherit_lot": False,
                        },
                    ),
                ],
            }
        )

    def test_update_quantities(self):
        manufacture = self.env["mrp.production"].create(
            {
                "product_id": self.result_product.id,
                "product_qty": 10.0,
                "bom_id": self.bom.id,
            }
        )
        manufacture.action_confirm()
        with Form(manufacture) as manufacture_form:
            manufacture_form.qty_producing = 0
        self.assertFalse(
            manufacture.move_byproduct_ids.filtered(
                lambda m: m.byproduct_id.inherit_lot
            ).move_line_ids
        )
        manufacture.action_generate_serial()
        lot = manufacture.lot_producing_ids
        serial = manufacture.lot_producing_ids.name
        with Form(manufacture) as manufacture_form:
            manufacture_form.qty_producing = 1
        manufacture.flush_recordset()
        self.assertTrue(
            manufacture.move_byproduct_ids.filtered(
                lambda m: m.byproduct_id.inherit_lot
            ).move_line_ids
        )
        for move in manufacture.move_byproduct_ids.filtered(
            lambda m: m.byproduct_id.inherit_lot
        ):
            self.assertEqual(1, len(move.move_line_ids))
            self.assertEqual(move.move_line_ids.lot_id.name, serial)
            self.assertNotEqual(move.move_line_ids.lot_id, lot)
            self.assertEqual(
                move.move_line_ids.lot_id.product_id, move.move_line_ids.product_id
            )
        with Form(manufacture) as manufacture_form:
            manufacture_form.qty_producing = 2
        manufacture.flush_recordset()
        self.assertTrue(
            manufacture.move_byproduct_ids.filtered(
                lambda m: m.byproduct_id.inherit_lot
            ).move_line_ids
        )
        for move in manufacture.move_byproduct_ids.filtered(
            lambda m: m.byproduct_id.inherit_lot
        ):
            self.assertEqual(move.move_line_ids.lot_id.name, serial)
            self.assertNotEqual(move.move_line_ids.lot_id, lot)
            self.assertEqual(
                move.move_line_ids.lot_id.product_id, move.move_line_ids.product_id
            )
            self.assertEqual(2, len(move.move_line_ids))

    def test_generate_serial(self):
        manufacture = self.env["mrp.production"].create(
            {
                "product_id": self.result_product.id,
                "product_qty": 10.0,
                "bom_id": self.bom.id,
            }
        )
        manufacture.action_confirm()
        with Form(manufacture) as manufacture_form:
            manufacture_form.qty_producing = 10
        manufacture.action_generate_serial()
        lot = manufacture.lot_producing_ids
        serial = manufacture.lot_producing_ids.name
        self.assertTrue(
            manufacture.move_byproduct_ids.filtered(
                lambda m: m.byproduct_id.inherit_lot
            ).move_line_ids
        )
        for move in manufacture.move_byproduct_ids.filtered(
            lambda m: m.byproduct_id.inherit_lot
        ):
            self.assertEqual(move.move_line_ids.lot_id.name, serial)
            self.assertNotEqual(move.move_line_ids.lot_id, lot)
            self.assertEqual(
                move.move_line_ids.lot_id.product_id, move.move_line_ids.product_id
            )
            self.assertEqual(1, len(move.move_line_ids))
