# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class TestQualityControlMrp(TransactionCase):
    def setUp(self):
        super().setUp()
        self.inspection_model = self.env["qc.inspection"]
        self.qc_trigger_model = self.env["qc.trigger"]
        self.test = self.env.ref("quality_control_oca.qc_test_1")
        self.trigger = self.env.ref("quality_control_mrp_oca.qc_trigger_mrp")
        # Category
        category_form = Form(self.env["product.category"])
        category_form.name = "Test category"
        self.category = category_form.save()
        # Product
        product_form = Form(self.env["product.template"])
        product_form.name = "Test Product"
        product_form.type = "product"
        self.product = product_form.save()
        # Materials
        product_form = Form(self.env["product.product"])
        product_form.name = "Part 1 Product"
        product_form.type = "product"
        self.mat1 = product_form.save()
        product_form = Form(self.env["product.product"])
        product_form.name = "Part 2 Product"
        product_form.type = "product"
        self.mat2 = product_form.save()
        # Bom
        bom_form = Form(self.env["mrp.bom"])
        bom_form.product_tmpl_id = self.product
        bom_form.product_qty = 1.0
        bom_form.type = "normal"
        with bom_form.bom_line_ids.new() as material_form:
            material_form.product_id = self.mat1
            material_form.product_qty = 1
        with bom_form.bom_line_ids.new() as material_form:
            material_form.product_id = self.mat2
            material_form.product_qty = 1
        self.bom = bom_form.save()
        # Production
        production_form = Form(self.env["mrp.production"])
        production_form.product_id = self.product.product_variant_id
        production_form.bom_id = self.bom
        production_form.product_qty = 2.0
        self.production1 = production_form.save()
        self.production1.action_confirm()
        self.production1.action_assign()
        # Inspection
        inspection_lines = self.inspection_model._prepare_inspection_lines(self.test)
        self.inspection1 = self.inspection_model.create(
            {"name": "Test Inspection", "inspection_lines": inspection_lines}
        )

    def test_inspection_create_for_product(self):
        self.product.product_variant_id.qc_triggers = [
            (0, 0, {"trigger": self.trigger.id, "test": self.test.id})
        ]
        produce_wizard = Form(
            self.env["mrp.product.produce"].with_context(
                {"active_id": self.production1.id, "active_ids": self.production1.ids}
            )
        )
        produce_wizard.qty_producing = self.production1.product_qty
        produce_wizard.save().do_produce()
        self.production1.post_inventory()
        self.assertEqual(
            self.production1.created_inspections,
            1,
            "Only one inspection must be created",
        )

    def test_inspection_create_for_template(self):
        self.product.qc_triggers = [
            (0, 0, {"trigger": self.trigger.id, "test": self.test.id})
        ]
        produce_wizard = Form(
            self.env["mrp.product.produce"].with_context(
                {"active_id": self.production1.id, "active_ids": self.production1.ids}
            )
        )
        produce_wizard.qty_producing = self.production1.product_qty
        produce_wizard.save().do_produce()
        self.production1.post_inventory()
        self.assertEqual(
            self.production1.created_inspections,
            1,
            "Only one inspection must be created",
        )

    def test_inspection_create_for_category(self):
        self.product.categ_id.qc_triggers = [
            (0, 0, {"trigger": self.trigger.id, "test": self.test.id})
        ]
        produce_wizard = Form(
            self.env["mrp.product.produce"].with_context(
                {"active_id": self.production1.id, "active_ids": self.production1.ids}
            )
        )
        produce_wizard.qty_producing = self.production1.product_qty
        produce_wizard.save().do_produce()
        self.production1.post_inventory()
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
        produce_wizard = Form(
            self.env["mrp.product.produce"].with_context(
                {"active_id": self.production1.id, "active_ids": self.production1.ids}
            )
        )
        produce_wizard.qty_producing = self.production1.product_qty
        produce_wizard.save().do_produce()
        self.production1.post_inventory()
        self.assertEqual(
            self.production1.created_inspections,
            1,
            "Only one inspection must be created",
        )

    def test_inspection_with_partial_fabrication(self):
        self.product.qc_triggers = [
            (0, 0, {"trigger": self.trigger.id, "test": self.test.id})
        ]
        produce_wizard = Form(
            self.env["mrp.product.produce"].with_context(
                {"active_id": self.production1.id, "active_ids": self.production1.ids}
            )
        )
        produce_wizard.qty_producing = 1.0
        produce_wizard.save().do_produce()
        self.production1.post_inventory()
        self.assertEqual(
            self.production1.created_inspections,
            1,
            "Only one inspection must be created.",
        )
        produce_wizard = Form(
            self.env["mrp.product.produce"].with_context(
                {"active_id": self.production1.id, "active_ids": self.production1.ids}
            )
        )
        produce_wizard.qty_producing = 1.0
        produce_wizard.save().do_produce()
        self.production1.post_inventory()
        self.assertEqual(
            self.production1.created_inspections, 2, "There must be only 2 inspections."
        )

    def test_qc_inspection_mo(self):
        self.inspection1.write(
            {"object_id": "%s,%d" % (self.production1._name, self.production1.id)}
        )
        self.assertEquals(self.inspection1.production_id, self.production1)
