# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import exceptions

from odoo.addons.base.tests.common import BaseCommon

from ..models.qc_trigger_line import _filter_trigger_lines


class TestQualityControlOcaBase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inspection_model = cls.env["qc.inspection"]
        cls.category_model = cls.env["qc.test.category"]
        cls.question_model = cls.env["qc.test.question"]
        cls.wizard_model = cls.env["qc.inspection.set.test"]
        cls.qc_trigger = cls.env["qc.trigger"].create({"name": "Test Trigger"})
        cls.test = cls.env.ref("quality_control_oca.qc_test_1")
        cls.val_ok = cls.env.ref("quality_control_oca.qc_test_question_value_1")
        cls.val_ko = cls.env.ref("quality_control_oca.qc_test_question_value_2")
        cls.qn_question = cls.env.ref("quality_control_oca.qc_test_question_2")
        cls.cat_generic = cls.env.ref(
            "quality_control_oca.qc_test_template_category_generic"
        )
        cls.product = cls.env["product.product"].create({"name": "Test product"})
        cls.inspection1 = cls.inspection_model.create(
            {
                "name": "Test Inspection",
                "inspection_lines": cls.inspection_model._prepare_inspection_lines(
                    cls.test
                ),
            }
        )


class TestQualityControlOca(TestQualityControlOcaBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard = cls.wizard_model.with_context(active_id=cls.inspection1.id).create(
            {"test": cls.test.id}
        )
        cls.wizard.action_create_test()
        cls.inspection1.action_todo()

    def test_inspection_correct(self):
        for line in self.inspection1.inspection_lines:
            if line.question_type == "qualitative":
                line.qualitative_value = self.val_ok
            if line.question_type == "quantitative":
                line.quantitative_value = 5.0
        self.inspection1.action_confirm()
        for line in self.inspection1.inspection_lines:
            self.assertTrue(
                line.success, "Incorrect state in inspection line %s" % line.name
            )
        self.assertTrue(
            self.inspection1.success,
            "Incorrect state in inspection %s" % self.inspection1.name,
        )
        self.assertEqual(self.inspection1.state, "success")
        self.inspection1.action_approve()
        self.assertEqual(self.inspection1.state, "success")
        self.assertTrue(bool(self.inspection1.date_done))
        self.inspection1.action_cancel()
        self.inspection1.action_draft()
        self.assertFalse(self.inspection1.date_done)

    def test_inspection_incorrect(self):
        for line in self.inspection1.inspection_lines:
            if line.question_type == "qualitative":
                line.qualitative_value = self.val_ko
            if line.question_type == "quantitative":
                line.quantitative_value = 15.0
        self.inspection1.action_confirm()
        for line in self.inspection1.inspection_lines:
            self.assertFalse(
                line.success, "Incorrect state in inspection line %s" % line.name
            )
        self.assertFalse(
            self.inspection1.success,
            "Incorrect state in inspection %s" % self.inspection1.name,
        )
        self.assertEqual(self.inspection1.state, "waiting")
        self.inspection1.action_approve()
        self.assertEqual(self.inspection1.state, "failed")
        self.assertTrue(bool(self.inspection1.date_done))

    def test_actions_errors(self):
        inspection2 = self.inspection1.copy()
        inspection2.action_draft()
        inspection2.write({"test": False})
        with self.assertRaises(exceptions.UserError):
            inspection2.action_todo()
        inspection3 = self.inspection1.copy()
        inspection3.write(
            {
                "inspection_lines": self.inspection_model._prepare_inspection_lines(
                    inspection3.test
                )
            }
        )
        for line in inspection3.inspection_lines:
            if line.question_type == "quantitative":
                line.quantitative_value = 15.0
        with self.assertRaises(exceptions.UserError):
            inspection3.action_confirm()
        inspection4 = self.inspection1.copy()
        inspection4.write(
            {
                "inspection_lines": self.inspection_model._prepare_inspection_lines(
                    inspection4.test
                )
            }
        )
        for line in inspection4.inspection_lines:
            if line.question_type == "quantitative":
                line.write({"uom_id": False, "quantitative_value": 15.0})
            elif line.question_type == "qualitative":
                line.qualitative_value = self.val_ok
        with self.assertRaises(exceptions.UserError):
            inspection4.action_confirm()

    def test_categories(self):
        category1 = self.category_model.create({"name": "Category ONE"})
        category2 = self.category_model.create(
            {"name": "Category TWO", "parent_id": category1.id}
        )
        self.assertEqual(
            category2.complete_name,
            f"{category1.name} / {category2.name}",
            "Something went wrong when computing complete name",
        )
        with self.assertRaises(exceptions.UserError):
            category1.parent_id = category2.id

    def test_get_qc_trigger_product(self):
        self.test.write({"fill_correct_values": True})
        trigger_lines = set()
        self.product.write(
            {
                "qc_triggers": [
                    (0, 0, {"trigger": self.qc_trigger.id, "test": self.test.id})
                ],
            }
        )
        self.product.product_tmpl_id.write(
            {
                "qc_triggers": [
                    (0, 0, {"trigger": self.qc_trigger.id, "test": self.test.id})
                ],
            }
        )
        self.product.categ_id.write(
            {
                "qc_triggers": [
                    (0, 0, {"trigger": self.qc_trigger.id, "test": self.test.id})
                ],
            }
        )
        for model in [
            "qc.trigger.product_category_line",
            "qc.trigger.product_template_line",
            "qc.trigger.product_line",
        ]:
            trigger_lines = trigger_lines.union(
                self.env[model].get_trigger_line_for_product(
                    self.qc_trigger, ["after"], self.product
                )
            )
        self.assertEqual(len(trigger_lines), 3)
        filtered_trigger_lines = _filter_trigger_lines(trigger_lines)
        self.assertEqual(len(filtered_trigger_lines), 1)
        for trigger_line in filtered_trigger_lines:
            inspection = self.inspection_model._make_inspection(
                self.product, trigger_line
            )
            self.assertEqual(inspection.state, "ready")
            self.assertTrue(inspection.auto_generated)
            self.assertEqual(inspection.test, self.test)
            for line in inspection.inspection_lines:
                if line.question_type == "qualitative":
                    self.assertEqual(line.qualitative_value, self.val_ok)
                elif line.question_type == "quantitative":
                    self.assertAlmostEqual(
                        round(line.quantitative_value, 2),
                        round(
                            (self.qn_question.min_value + self.qn_question.max_value)
                            * 0.5,
                            2,
                        ),
                    )

    def test_qc_inspection_not_draft_unlink(self):
        with self.assertRaises(exceptions.UserError):
            self.inspection1.unlink()
        inspection2 = self.inspection1.copy()
        inspection2.action_cancel()
        self.assertEqual(inspection2.state, "canceled")
        inspection2.action_draft()
        self.assertEqual(inspection2.state, "draft")
        inspection2.unlink()

    def test_qc_inspection_auto_generate_unlink(self):
        inspection2 = self.inspection1.copy()
        inspection2.write({"auto_generated": True})
        with self.assertRaises(exceptions.UserError):
            inspection2.unlink()

    def test_qc_inspection_product(self):
        self.inspection1.write(
            {"object_id": "%s,%d" % (self.product._name, self.product.id)}
        )
        self.assertEqual(self.inspection1.product_id, self.product)

    def test_qc_test_question_constraints(self):
        with self.assertRaises(exceptions.ValidationError):
            self.question_model.create(
                {
                    "name": "Quantitative Question",
                    "type": "quantitative",
                    "min_value": 1.0,
                    "max_value": 0.0,
                }
            )
        with self.assertRaises(exceptions.ValidationError):
            self.question_model.create(
                {
                    "name": "Qualitative Question",
                    "type": "qualitative",
                    "ql_values": [(0, 0, {"name": "Qualitative answer", "ok": False})],
                }
            )
