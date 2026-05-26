# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestMrpProductionCheckBomAlignment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.final_product = cls.env["product.product"].create(
            {"name": "Final Product", "is_storable": True}
        )
        cls.component_1 = cls.env["product.product"].create(
            {"name": "Component 1", "is_storable": True}
        )
        cls.component_2 = cls.env["product.product"].create(
            {"name": "Component 2", "is_storable": True}
        )
        cls.component_3 = cls.env["product.product"].create(
            {"name": "Component 3", "is_storable": True}
        )
        cls.byproduct_product = cls.env["product.product"].create(
            {"name": "By-product 1", "is_storable": True}
        )
        cls.byproduct_product_2 = cls.env["product.product"].create(
            {"name": "By-product 2", "is_storable": True}
        )

        cls.workcenter_1 = cls.env["mrp.workcenter"].create({"name": "Workcenter 1"})
        cls.workcenter_2 = cls.env["mrp.workcenter"].create({"name": "Workcenter 2"})

        cls.test_bom = cls.env["mrp.bom"].create(
            {
                "product_id": cls.final_product.id,
                "product_tmpl_id": cls.final_product.product_tmpl_id.id,
                "product_uom_id": cls.final_product.uom_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )

        cls.operation_1 = cls.env["mrp.routing.workcenter"].create(
            {
                "name": "Operation 1",
                "workcenter_id": cls.workcenter_1.id,
                "bom_id": cls.test_bom.id,
            }
        )
        cls.operation_2 = cls.env["mrp.routing.workcenter"].create(
            {
                "name": "Operation 2",
                "workcenter_id": cls.workcenter_2.id,
                "bom_id": cls.test_bom.id,
            }
        )

        cls.bom_line_1 = cls.env["mrp.bom.line"].create(
            {
                "bom_id": cls.test_bom.id,
                "product_id": cls.component_1.id,
                "product_qty": 2.0,
                "operation_id": cls.operation_1.id,
            }
        )
        cls.bom_line_2 = cls.env["mrp.bom.line"].create(
            {
                "bom_id": cls.test_bom.id,
                "product_id": cls.component_2.id,
                "product_qty": 1.0,
                "operation_id": cls.operation_1.id,
            }
        )
        cls.bom_byproduct = cls.env["mrp.bom.byproduct"].create(
            {
                "bom_id": cls.test_bom.id,
                "product_id": cls.byproduct_product.id,
                "product_qty": 1.0,
                "product_uom_id": cls.byproduct_product.uom_id.id,
                "operation_id": cls.operation_1.id,
            }
        )

    @classmethod
    def _create_mo(cls, bom=None, qty=1.0):
        mo = cls.env["mrp.production"].create(
            {
                "product_id": cls.final_product.id,
                "product_qty": qty,
                "bom_id": (bom or cls.test_bom).id,
            }
        )
        mo.action_confirm()
        return mo

    def test_aligned_returns_false(self):
        mo = self._create_mo()
        self.assertFalse(mo._get_bom_alignment_error(mo.name))

    def test_bom_component_added_returns_error(self):
        mo = self._create_mo()
        self.test_bom.bom_line_ids = [
            Command.create({"product_id": self.component_3.id, "product_qty": 1.0})
        ]
        self.assertTrue(mo.is_outdated_bom)
        self.assertTrue(mo._get_bom_alignment_error(mo.name))

    def test_bom_operation_added_returns_error(self):
        mo = self._create_mo()
        self.env["mrp.routing.workcenter"].create(
            {
                "name": "Extra Operation",
                "workcenter_id": self.workcenter_2.id,
                "bom_id": self.test_bom.id,
            }
        )
        self.assertTrue(mo._get_bom_alignment_error(mo.name))

    def test_component_qty_changed_returns_error(self):
        mo = self._create_mo()
        self.bom_line_1.product_qty += 1.0
        self.assertTrue(mo._get_bom_alignment_error(mo.name))

    def test_consumed_at_operation_changed_returns_error(self):
        mo = self._create_mo()
        self.bom_line_1.operation_id = self.operation_2
        self.assertTrue(mo._get_bom_alignment_error(mo.name))

    def test_action_confirm_aligned_confirms_mo(self):
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.final_product.id,
                "product_qty": 1.0,
                "bom_id": self.test_bom.id,
            }
        )
        result = mo.action_confirm()
        self.assertEqual(result, True)
        self.assertEqual(mo.state, "confirmed")

    def test_action_confirm_misaligned_returns_wizard(self):
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.final_product.id,
                "product_qty": 1.0,
                "bom_id": self.test_bom.id,
            }
        )
        self.bom_line_1.product_qty += 1.0
        result = mo.action_confirm()
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("res_model"), "mrp.bom.alignment.warning")
        self.assertEqual(mo.state, "draft")

    def test_action_confirm_skip_check_confirms_despite_misalignment(self):
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.final_product.id,
                "product_qty": 1.0,
                "bom_id": self.test_bom.id,
            }
        )
        self.bom_line_1.product_qty += 1.0
        mo.with_context(skip_bom_alignment_check=True).action_confirm()
        self.assertEqual(mo.state, "confirmed")

    def test_bom_alignment_warning_set_when_misaligned(self):
        mo = self._create_mo()
        self.assertFalse(mo.bom_alignment_warning)
        self.bom_line_1.product_qty += 1.0
        mo.invalidate_recordset(["bom_alignment_warning"])
        self.assertTrue(mo.bom_alignment_warning)

    def test_bom_alignment_warning_empty_when_done(self):
        mo = self._create_mo()
        self.bom_line_1.product_qty += 1.0
        mo.state = "done"
        mo.invalidate_recordset(["bom_alignment_warning"])
        self.assertFalse(mo.bom_alignment_warning)

    def test_bom_byproduct_added_returns_error(self):
        mo = self._create_mo()
        self.test_bom.byproduct_ids = [
            Command.create(
                {
                    "product_id": self.byproduct_product_2.id,
                    "product_qty": 1.0,
                    "product_uom_id": self.byproduct_product_2.uom_id.id,
                }
            )
        ]
        self.assertTrue(mo._get_bom_alignment_error(mo.name))

    def test_byproduct_qty_changed_returns_error(self):
        mo = self._create_mo()
        self.bom_byproduct.product_qty += 1.0
        self.assertTrue(mo._get_bom_alignment_error(mo.name))

    def test_produced_at_operation_changed_returns_error(self):
        mo = self._create_mo()
        self.bom_byproduct.operation_id = self.operation_2
        self.assertTrue(mo._get_bom_alignment_error(mo.name))

    def test_action_update_and_confirm(self):
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.final_product.id,
                "product_qty": 1.0,
                "bom_id": self.test_bom.id,
            }
        )
        self.test_bom.bom_line_ids = [
            Command.create({"product_id": self.component_3.id, "product_qty": 1.0})
        ]
        self.assertTrue(mo.is_outdated_bom)
        wizard_action = mo.action_confirm()
        self.assertEqual(wizard_action.get("res_model"), "mrp.bom.alignment.warning")
        wizard = self.env["mrp.bom.alignment.warning"].browse(wizard_action["res_id"])
        wizard.action_update_and_confirm()
        self.assertEqual(mo.state, "confirmed")
        self.assertFalse(mo.is_outdated_bom)
        self.assertFalse(mo._get_bom_alignment_error(mo.name))
