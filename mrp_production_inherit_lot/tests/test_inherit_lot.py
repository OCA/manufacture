# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command
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
                    Command.create(
                        {
                            "product_id": cls.sub_product_01.id,
                            "inherit_lot": True,
                        },
                    ),
                    Command.create(
                        {
                            "product_id": cls.sub_product_02.id,
                            "inherit_lot": True,
                        },
                    ),
                    Command.create(
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

    def _create_untracked_byproduct_production(self):
        untracked_product = self.env["product.product"].create(
            {"name": "Untracked Sub Product", "is_storable": True, "tracking": "none"}
        )
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.result_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "byproduct_ids": [
                    Command.create(
                        {
                            "product_id": self.sub_product_01.id,
                            "inherit_lot": True,
                        },
                    ),
                    Command.create(
                        {
                            "product_id": untracked_product.id,
                            "inherit_lot": True,
                        },
                    ),
                ],
            }
        )
        manufacture = self.env["mrp.production"].create(
            {
                "product_id": self.result_product.id,
                "product_qty": 10.0,
                "bom_id": bom.id,
            }
        )
        manufacture.action_confirm()
        return manufacture, untracked_product

    def _check_untracked_byproduct(self, manufacture, untracked_product):
        serial = manufacture.lot_producing_ids.name
        tracked_move = manufacture.move_byproduct_ids.filtered(
            lambda m: m.product_id == self.sub_product_01
        )
        untracked_move = manufacture.move_byproduct_ids.filtered(
            lambda m: m.product_id == untracked_product
        )
        self.assertEqual(tracked_move.move_line_ids.lot_id.name, serial)
        self.assertTrue(untracked_move.move_line_ids)
        self.assertFalse(untracked_move.move_line_ids.lot_id)
        self.assertFalse(
            self.env["stock.lot"].search([("product_id", "=", untracked_product.id)])
        )

    def test_untracked_byproduct_update_quantities(self):
        manufacture, untracked_product = self._create_untracked_byproduct_production()
        with Form(manufacture) as manufacture_form:
            manufacture_form.qty_producing = 0
        manufacture.action_generate_serial()
        with Form(manufacture) as manufacture_form:
            manufacture_form.qty_producing = 1
        manufacture.flush_recordset()
        self._check_untracked_byproduct(manufacture, untracked_product)

    def test_untracked_byproduct_generate_serial(self):
        manufacture, untracked_product = self._create_untracked_byproduct_production()
        with Form(manufacture) as manufacture_form:
            manufacture_form.qty_producing = 10
        manufacture.action_generate_serial()
        self._check_untracked_byproduct(manufacture, untracked_product)

    def _create_multicompany_production(self, existing_lot_company):
        """Produce in a second company with a byproduct lot named as the
        producing lot already existing in ``existing_lot_company``."""
        company_b = self.env["res.company"].create({"name": "Inherit Lot Company B"})
        existing_lot = self.env["stock.lot"].create(
            {
                "name": "MC-LOT",
                "product_id": self.sub_product_01.id,
                "company_id": existing_lot_company(company_b).id,
            }
        )
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.result_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "company_id": company_b.id,
                "byproduct_ids": [
                    Command.create(
                        {
                            "product_id": self.sub_product_01.id,
                            "inherit_lot": True,
                        },
                    ),
                ],
            }
        )
        manufacture = (
            self.env["mrp.production"]
            .with_company(company_b)
            .create(
                {
                    "product_id": self.result_product.id,
                    "product_qty": 10.0,
                    "bom_id": bom.id,
                    "company_id": company_b.id,
                }
            )
        )
        manufacture.action_confirm()
        with Form(manufacture) as manufacture_form:
            manufacture_form.qty_producing = 0
        manufacture.lot_producing_ids = self.env["stock.lot"].create(
            {
                "name": "MC-LOT",
                "product_id": self.result_product.id,
                "company_id": company_b.id,
            }
        )
        with Form(manufacture) as manufacture_form:
            manufacture_form.qty_producing = 1
        manufacture.flush_recordset()
        byproduct_lot = manufacture.move_byproduct_ids.move_line_ids.lot_id
        self.assertEqual(1, len(byproduct_lot))
        self.assertEqual(byproduct_lot.name, "MC-LOT")
        self.assertEqual(byproduct_lot.product_id, self.sub_product_01)
        return company_b, existing_lot, byproduct_lot

    def test_multicompany_ignore_other_company_lot(self):
        company_b, existing_lot, byproduct_lot = self._create_multicompany_production(
            lambda company_b: self.env.company
        )
        self.assertNotEqual(byproduct_lot, existing_lot)
        self.assertEqual(byproduct_lot.company_id, company_b)

    def test_multicompany_reuse_same_company_lot(self):
        company_b, existing_lot, byproduct_lot = self._create_multicompany_production(
            lambda company_b: company_b
        )
        self.assertEqual(byproduct_lot, existing_lot)

    def test_multicompany_reuse_shared_lot(self):
        company_b, existing_lot, byproduct_lot = self._create_multicompany_production(
            lambda company_b: self.env["res.company"]
        )
        self.assertEqual(byproduct_lot, existing_lot)
