# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2018 Simone Rubino - Agile Business Group
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
        # Inspection
        inspection_lines = cls.inspection_model._prepare_inspection_lines(cls.test)
        cls.inspection1 = cls.inspection_model.create(
            {"name": "Test Inspection", "inspection_lines": inspection_lines}
        )

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
