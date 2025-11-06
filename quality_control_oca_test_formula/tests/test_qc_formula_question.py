# Copyright 2025 Binhex - Ariel Brreiros
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase

from odoo.addons.quality_control_oca_test_formula.models.qc_test import (
    FORMULA_TEMPLATE,
)


class TestQcFormulaQuestion(TransactionCase):
    def setUp(self):
        super().setUp()
        self.qc_test = self.env["qc.test"].create(
            {
                "name": "Formula-enabled Test",
                "type": "generic",
            }
        )
        self.uom_unit = self.env.ref("uom.product_uom_unit")

    def _create_inspection_line(self, question, state="ready"):
        inspection = self.env["qc.inspection"].create(
            {
                "name": "Inspection",
                "test": self.qc_test.id,
                "state": state,
            }
        )
        values = {
            "inspection_id": inspection.id,
            "name": question.name,
            "test_line": question.id,
            "question_type": question.type,
        }
        if question.type == "qualitative" and question.ql_values:
            values["possible_ql_values"] = [(6, 0, question.ql_values.ids)]
        if question.type == "quantitative":
            if hasattr(question, "min_value"):
                values["min_value"] = question.min_value
            if hasattr(question, "max_value"):
                values["max_value"] = question.max_value
            if question.uom_id:
                values["test_uom_id"] = question.uom_id.id
                values["uom_id"] = question.uom_id.id
        line = self.env["qc.inspection.line"].create(values)
        if question.auto_compute_formula and state == "ready":
            line._apply_formula_auto_value()
        return inspection, line

    def test_quantitative_formula_populates_value_and_success(self):
        question = self.env["qc.test.question"].create(
            {
                "name": "Auto measurement",
                "test": self.qc_test.id,
                "type": "quantitative",
                "min_value": 5.0,
                "max_value": 10.0,
                "auto_compute_formula": True,
                "formula_code": "result = 8.25",
            }
        )
        inspection, line = self._create_inspection_line(question)
        self.assertAlmostEqual(line.quantitative_value, 8.25)
        self.assertTrue(line.success)

    def test_quantitative_formula_recompute_button(self):
        question = self.env["qc.test.question"].create(
            {
                "name": "Auto measurement",
                "test": self.qc_test.id,
                "type": "quantitative",
                "min_value": 1.0,
                "max_value": 5.0,
                "auto_compute_formula": True,
                "formula_code": "result = 3.0",
            }
        )
        inspection, line = self._create_inspection_line(question)
        line.write({"quantitative_value": 1.0})
        inspection.action_recompute_formula_lines()
        line.invalidate_recordset()
        self.assertEqual(line.quantitative_value, 3.0)

    def test_quantitative_formula_manual_override(self):
        question = self.env["qc.test.question"].create(
            {
                "name": "Override allowed",
                "test": self.qc_test.id,
                "type": "quantitative",
                "min_value": 1.0,
                "max_value": 10.0,
                "auto_compute_formula": True,
                "formula_code": "result = 4.0",
            }
        )
        inspection, line = self._create_inspection_line(question)
        self.assertEqual(line.quantitative_value, 4.0)

        line.write({"quantitative_value": 9.0})
        line.invalidate_recordset()
        self.assertEqual(line.quantitative_value, 9.0)

        inspection.action_recompute_formula_lines()
        line.invalidate_recordset()
        self.assertEqual(line.quantitative_value, 4.0)

    def test_quantitative_formula_invalid_value(self):
        question = self.env["qc.test.question"].create(
            {
                "name": "Bad value",
                "test": self.qc_test.id,
                "type": "quantitative",
                "auto_compute_formula": True,
                "formula_code": "result = 'not a number'",
            }
        )
        inspection, line = self._create_inspection_line(question, state="draft")
        with self.assertRaises(UserError):
            line._apply_formula_auto_value()

    def test_formula_syntax_validation(self):
        with self.assertRaises(ValidationError):
            self.env["qc.test.question"].create(
                {
                    "name": "Broken",
                    "test": self.qc_test.id,
                    "type": "quantitative",
                    "auto_compute_formula": True,
                    "formula_code": "result = (",
                }
            )

    def test_qualitative_formula_with_boolean(self):
        question = self.env["qc.test.question"].create(
            {
                "name": "Check status",
                "test": self.qc_test.id,
                "type": "qualitative",
                "auto_compute_formula": True,
                "formula_code": "result = True",
            }
        )
        ok_value = self.env["qc.test.question.value"].create(
            {
                "test_line": question.id,
                "name": "OK",
                "ok": True,
            }
        )
        self.env["qc.test.question.value"].create(
            {
                "test_line": question.id,
                "name": "KO",
                "ok": False,
            }
        )
        inspection, line = self._create_inspection_line(question)
        line._compute_quality_test_check()
        line.invalidate_recordset()
        self.assertEqual(line.qualitative_value, ok_value)
        self.assertTrue(line.success)

    def test_qualitative_formula_with_name(self):
        question = self.env["qc.test.question"].create(
            {
                "name": "Choose name",
                "test": self.qc_test.id,
                "type": "qualitative",
                "auto_compute_formula": True,
                "formula_code": "result = 'Manual Choice'",
            }
        )
        self.env["qc.test.question.value"].create(
            {
                "test_line": question.id,
                "name": "Manual Choice",
                "ok": True,
            }
        )
        inspection, line = self._create_inspection_line(question)
        line._compute_quality_test_check()
        line.invalidate_recordset()
        self.assertEqual(line.qualitative_value.name, "Manual Choice")

    def test_qualitative_formula_with_unmatched_name(self):
        question = self.env["qc.test.question"].create(
            {
                "name": "Unknown name",
                "test": self.qc_test.id,
                "type": "qualitative",
                "auto_compute_formula": True,
                "formula_code": "result = 'Missing'",
            }
        )
        self.env["qc.test.question.value"].create(
            {
                "test_line": question.id,
                "name": "Existing",
                "ok": True,
            }
        )
        inspection, line = self._create_inspection_line(question)
        self.assertFalse(line._apply_formula_auto_value())
        self.assertFalse(line.qualitative_value)

    def test_onchange_auto_compute_injects_template(self):
        question = self.env["qc.test.question"].new(
            {
                "name": "Draft",
                "test": self.qc_test,
                "type": "quantitative",
                "auto_compute_formula": True,
            }
        )
        question.formula_code = False
        question._onchange_auto_compute_formula()
        self.assertEqual(question.formula_code, FORMULA_TEMPLATE)

    def test_formula_requires_result_assignment(self):
        question = self.env["qc.test.question"].create(
            {
                "name": "Missing result",
                "test": self.qc_test.id,
                "type": "quantitative",
                "auto_compute_formula": True,
                "formula_code": "# only comments",
            }
        )
        _inspection, line = self._create_inspection_line(question, state="draft")
        with self.assertRaises(UserError):
            line._apply_formula_auto_value()

    def test_formula_exception_is_wrapped_in_user_error(self):
        question = self.env["qc.test.question"].create(
            {
                "name": "Exploding",
                "test": self.qc_test.id,
                "type": "quantitative",
                "auto_compute_formula": True,
                "formula_code": "raise ValueError('boom')",
            }
        )
        _inspection, line = self._create_inspection_line(question, state="draft")
        with self.assertRaises(UserError) as err:
            line._apply_formula_auto_value()
        self.assertIn("boom", str(err.exception))

    def test_quantitative_formula_normalizes_zero_and_sets_uom(self):
        question = self.env["qc.test.question"].create(
            {
                "name": "Zero normalize",
                "test": self.qc_test.id,
                "type": "quantitative",
                "uom_id": self.uom_unit.id,
                "auto_compute_formula": True,
                "formula_code": "result = 0",
            }
        )
        _inspection, line = self._create_inspection_line(question)
        self.assertEqual(line.quantitative_value, 0.0)
        self.assertEqual(line.uom_id, self.uom_unit)

    def test_qualitative_formula_with_boolean_false(self):
        question = self.env["qc.test.question"].create(
            {
                "name": "False pick",
                "test": self.qc_test.id,
                "type": "qualitative",
                "auto_compute_formula": True,
                "formula_code": "result = False",
            }
        )
        self.env["qc.test.question.value"].create(
            {
                "test_line": question.id,
                "name": "OK",
                "ok": True,
            }
        )
        ko_value = self.env["qc.test.question.value"].create(
            {
                "test_line": question.id,
                "name": "KO",
                "ok": False,
            }
        )
        _inspection, line = self._create_inspection_line(question)
        line._compute_quality_test_check()
        line.invalidate_recordset()
        self.assertEqual(line.qualitative_value, ko_value)

    def test_qualitative_formula_with_invalid_type(self):
        question = self.env["qc.test.question"].create(
            {
                "name": "Invalid",
                "test": self.qc_test.id,
                "type": "qualitative",
                "auto_compute_formula": True,
                "formula_code": "result = 42",
            }
        )
        inspection, line = self._create_inspection_line(question, state="draft")
        self.assertFalse(line._apply_formula_auto_value())
        self.assertFalse(line.qualitative_value)

    def test_formula_appends_log_to_internal_notes(self):
        question = self.env["qc.test.question"].create(
            {
                "name": "Log writer",
                "test": self.qc_test.id,
                "type": "quantitative",
                "auto_compute_formula": True,
                "formula_code": "result = 5\nmessage = 'Auto fill log'",
            }
        )
        inspection, _line = self._create_inspection_line(question)
        self.assertIn("Auto fill log", inspection.internal_notes)

    def test_quality_test_check_triggers_auto_compute(self):
        question = self.env["qc.test.question"].create(
            {
                "name": "Deferred compute",
                "test": self.qc_test.id,
                "type": "quantitative",
                "min_value": 1.0,
                "max_value": 10.0,
                "auto_compute_formula": True,
                "formula_code": "result = 7.5",
            }
        )
        inspection, line = self._create_inspection_line(question, state="draft")
        self.assertFalse(line.auto_computed)
        inspection.state = "ready"
        inspection.invalidate_recordset()
        line.invalidate_recordset()
        line._compute_quality_test_check()
        line.invalidate_recordset()
        self.assertAlmostEqual(line.quantitative_value, 7.5)
        self.assertTrue(line.auto_computed)
        self.assertTrue(line.success)

    def test_has_auto_compute_formula_lines_flag(self):
        question = self.env["qc.test.question"].create(
            {
                "name": "Recompute flag",
                "test": self.qc_test.id,
                "type": "quantitative",
                "auto_compute_formula": True,
                "formula_code": "result = 2.0",
            }
        )
        inspection, line = self._create_inspection_line(question)
        inspection.invalidate_recordset()
        self.assertFalse(inspection.has_auto_compute_formula_lines)

        line.write({"quantitative_value": 9.0})
        inspection.invalidate_recordset()
        self.assertTrue(inspection.has_auto_compute_formula_lines)

        inspection.action_recompute_formula_lines()
        inspection.invalidate_recordset()
        line.invalidate_recordset()
        self.assertEqual(line.quantitative_value, 2.0)
        self.assertFalse(inspection.has_auto_compute_formula_lines)
