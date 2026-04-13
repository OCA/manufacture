# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2018 Simone Rubino - Agile Business Group
# Copyright 2026 FactorLibre - Adriana Saiz <adriana.saiz@factorlibre.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form

from odoo.addons.quality_control_oca.tests.test_quality_control import (
    TestQualityControlOcaBase,
)


class TestQualityControlMrp(TestQualityControlOcaBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.trigger = cls.env.ref("quality_control_mrp_oca.qc_trigger_mrp")
        # Materials
        product_form = Form(cls.env["product.product"])
        product_form.name = "Part 1 Product"
        cls.mat1 = product_form.save()
        product_form = Form(cls.env["product.product"])
        product_form.name = "Part 2 Product"
        cls.mat2 = product_form.save()
        # Bom
        bom_form = Form(cls.env["mrp.bom"])
        bom_form.product_tmpl_id = cls.product.product_tmpl_id
        bom_form.product_qty = 1.0
        bom_form.type = "normal"
        with bom_form.bom_line_ids.new() as material_form:
            material_form.product_id = cls.mat1
            material_form.product_qty = 1
        with bom_form.bom_line_ids.new() as material_form:
            material_form.product_id = cls.mat2
            material_form.product_qty = 1
        cls.bom = bom_form.save()
        # Production
        production_form = Form(cls.env["mrp.production"])
        production_form.product_id = cls.product.product_variant_id
        production_form.bom_id = cls.bom
        production_form.product_qty = 2.0
        cls.production1 = production_form.save()
        cls.production1.action_confirm()
        cls.production1.action_assign()
        # Picking type trigger (auto-created by quality_control_stock_oca)
        cls.picking_type_trigger = cls.env["qc.trigger"].search(
            [("picking_type_id", "=", cls.production1.picking_type_id.id)], limit=1
        )
        # Inspection
        inspection_lines = cls.inspection_model._prepare_inspection_lines(cls.test)
        cls.inspection1 = cls.inspection_model.create(
            {"name": "Test Inspection", "inspection_lines": inspection_lines}
        )

    def _create_production(self, qty=2.0):
        """Helper to create a fresh production order."""
        production_form = Form(self.env["mrp.production"])
        production_form.product_id = self.product.product_variant_id
        production_form.bom_id = self.bom
        production_form.product_qty = qty
        production = production_form.save()
        return production

    def test_inspection_create_for_product(self):
        self.product.product_variant_id.qc_triggers = [
            (0, 0, {"trigger": self.trigger.id, "test": self.test.id})
        ]
        self.production1.qty_producing = self.production1.product_qty
        self.production1._post_inventory()
        self.assertEqual(
            self.production1.created_inspections,
            1,
            "Only one inspection must be created",
        )

    def test_inspection_create_for_template(self):
        self.product.qc_triggers = [
            (0, 0, {"trigger": self.trigger.id, "test": self.test.id})
        ]
        self.production1.qty_producing = self.production1.product_qty
        self.production1._post_inventory()
        self.assertEqual(
            self.production1.created_inspections,
            1,
            "Only one inspection must be created",
        )

    def test_inspection_create_for_category(self):
        self.product.categ_id.qc_triggers = [
            (0, 0, {"trigger": self.trigger.id, "test": self.test.id})
        ]
        self.production1.qty_producing = self.production1.product_qty
        self.production1._post_inventory()
        self.assertEqual(
            self.production1.created_inspections,
            1,
            "Only one inspection must be created",
        )

    def test_inspection_create_only_one(self):
        self.product.qc_triggers = [
            (0, 0, {"trigger": self.trigger.id, "test": self.test.id})
        ]
        self.product.categ_id.qc_triggers = [
            (0, 0, {"trigger": self.trigger.id, "test": self.test.id})
        ]
        self.production1.qty_producing = self.production1.product_qty
        self.production1._post_inventory()
        self.assertEqual(
            self.production1.created_inspections,
            1,
            "Only one inspection must be created",
        )

    def test_inspection_with_partial_fabrication(self):
        self.product.qc_triggers = [
            (0, 0, {"trigger": self.trigger.id, "test": self.test.id})
        ]
        self.production1.qty_producing = 1.0
        self.production1._post_inventory()
        self.assertEqual(
            self.production1.created_inspections,
            1,
            "Only one inspection must be created.",
        )
        self.production1.qty_producing = self.production1.product_qty
        self.production1._post_inventory()
        self.assertEqual(
            self.production1.created_inspections, 2, "There must be only 2 inspections."
        )

    def test_qc_inspection_mo(self):
        self.inspection1.write(
            {"object_id": "%s,%d" % (self.production1._name, self.production1.id)}
        )
        self.assertEqual(self.inspection1.production_id, self.production1)

    def test_after_with_picking_type_trigger(self):
        """After inspection is created using the picking type trigger."""
        self.assertTrue(
            self.picking_type_trigger,
            "Picking type trigger should exist for manufacturing operation",
        )
        self.product.product_variant_id.qc_triggers = [
            (
                0,
                0,
                {
                    "trigger": self.picking_type_trigger.id,
                    "test": self.test.id,
                    "timing": "after",
                },
            )
        ]
        production = self._create_production()
        production.action_confirm()
        production.action_assign()
        # No inspection yet (timing is after)
        self.assertEqual(production.created_inspections, 0)
        production.qty_producing = production.product_qty
        production._post_inventory()
        self.assertEqual(
            production.created_inspections,
            1,
            "One inspection should be created with after timing",
        )
        inspection = production.qc_inspections_ids
        self.assertEqual(inspection.state, "ready")

    def test_plan_ahead_creates_and_transitions(self):
        """Plan ahead creates PLAN on confirm and transitions to READY on done."""
        self.assertTrue(
            self.picking_type_trigger,
            "Picking type trigger should exist for manufacturing operation",
        )
        self.product.product_variant_id.qc_triggers = [
            (
                0,
                0,
                {
                    "trigger": self.picking_type_trigger.id,
                    "test": self.test.id,
                    "timing": "plan_ahead",
                },
            )
        ]
        production = self._create_production()
        production.action_confirm()
        # Inspection should be created in PLAN state by stock.move._action_confirm
        self.assertEqual(production.created_inspections, 1)
        inspection = production.qc_inspections_ids
        self.assertEqual(inspection.state, "plan")
        # Mark done — should transition to READY
        production.action_assign()
        production.qty_producing = production.product_qty
        production._post_inventory()
        self.assertEqual(inspection.state, "ready")
        # No duplicate inspection should be created
        self.assertEqual(production.created_inspections, 1)

    def test_before_timing(self):
        """Before inspection is created at confirm time."""
        self.assertTrue(
            self.picking_type_trigger,
            "Picking type trigger should exist for manufacturing operation",
        )
        self.product.product_variant_id.qc_triggers = [
            (
                0,
                0,
                {
                    "trigger": self.picking_type_trigger.id,
                    "test": self.test.id,
                    "timing": "before",
                },
            )
        ]
        production = self._create_production()
        production.action_confirm()
        self.assertEqual(production.created_inspections, 1)
        inspection = production.qc_inspections_ids
        self.assertEqual(inspection.state, "ready")

    def test_cancel_production_cancels_plan_inspections(self):
        """Cancelling production cancels plan inspections."""
        self.assertTrue(
            self.picking_type_trigger,
            "Picking type trigger should exist for manufacturing operation",
        )
        self.product.product_variant_id.qc_triggers = [
            (
                0,
                0,
                {
                    "trigger": self.picking_type_trigger.id,
                    "test": self.test.id,
                    "timing": "plan_ahead",
                },
            )
        ]
        production = self._create_production()
        production.action_confirm()
        inspection = production.qc_inspections_ids
        self.assertEqual(inspection.state, "plan")
        production.action_cancel()
        self.assertEqual(inspection.state, "canceled")

    def test_plan_ahead_and_after_combined_mo(self):
        """plan_ahead + after on same product creates 2 inspections on MO."""
        self.assertTrue(
            self.picking_type_trigger,
            "Picking type trigger should exist for manufacturing operation",
        )
        test2 = self.test.copy({"name": "Test After MO"})
        self.product.product_variant_id.qc_triggers = [
            (
                0,
                0,
                {
                    "trigger": self.picking_type_trigger.id,
                    "test": self.test.id,
                    "timing": "plan_ahead",
                },
            ),
            (
                0,
                0,
                {
                    "trigger": self.picking_type_trigger.id,
                    "test": test2.id,
                    "timing": "after",
                },
            ),
        ]
        production = self._create_production()
        production.action_confirm()
        # plan_ahead creates inspection in PLAN
        self.assertEqual(production.created_inspections, 1)
        plan_inspection = production.qc_inspections_ids
        self.assertEqual(plan_inspection.state, "plan")
        self.assertEqual(plan_inspection.timing, "plan_ahead")
        # Mark done — plan transitions to ready + after is created
        production.action_assign()
        production.qty_producing = production.product_qty
        production._post_inventory()
        self.assertEqual(production.created_inspections, 2)
        self.assertEqual(plan_inspection.state, "ready")
        after_inspection = production.qc_inspections_ids.filtered(
            lambda i: i.timing == "after"
        )
        self.assertEqual(len(after_inspection), 1)
        self.assertEqual(after_inspection.state, "ready")
