#  -*- coding: utf-8 -*-
#  Copyright 2019 Simone Rubino - Agile Business Group
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestQualityControlFormula(TransactionCase):

    def setUp(self):
        super(TestQualityControlFormula, self).setUp()
        test_model = self.env['qc.test']
        self.inspection_model = self.env['qc.inspection']
        self.wizard_model = self.env['qc.inspection.set.test']

        self.test = test_model.create({
            'name': 'Test',
            'test_lines': [
                (0, 0, self._prepare_question_values('A')),
                (0, 0, self._prepare_question_values('B')),
                (0, 0, self._prepare_question_values(
                    'C', 'A + B + int(input_value)')),
                (0, 0, self._prepare_question_values(
                    'D', 'C * int(input_value)'))
            ]
        })

    @staticmethod
    def _prepare_question_values(code, formula=''):
        return {
            'code': code,
            'name': 'Question ' + code,
            'formula': formula,
            'type': 'quantitative',
            'min_value': 0.0,
            'max_value': 10.0,
            'uom_id': 1
        }

    def _create_inspection(self, test):
        inspection = self.inspection_model.create({'name': 'Test inspection'})
        wizard = self.wizard_model.with_context(active_id=inspection.id) \
            .create({'test': test.id})
        wizard.action_create_test()
        return inspection

    def test_values_propagation(self):
        inspection = self._create_inspection(self.test)

        for inspection_line in inspection.inspection_lines:
            test_line = inspection_line.test_line
            self.assertEqual(test_line.code, inspection_line.code)
            self.assertEqual(test_line.formula, inspection_line.formula)
            self.assertEqual(test_line.sequence, inspection_line.sequence)

    def test_formula_evaluation_ok(self):
        inspection = self._create_inspection(self.test)

        value_a, value_b, value_c, value_d = 1, 2, "3", "4"

        # Initialize lines values
        for line in inspection.inspection_lines:
            if line.code == 'A':
                line.quantitative_value = value_a
            elif line.code == 'B':
                line.quantitative_value = value_b
            elif line.code == 'C':
                line.input_value = value_c
            elif line.code == 'D':
                line.input_value = value_d

        inspection.calculate_lines_values()

        inspection_line_d = inspection.inspection_lines \
            .filtered(lambda l: l.code == 'D')
        expected_res = (value_a + value_b + int(value_c)) * int(value_d)
        self.assertEqual(
            int(inspection_line_d.quantitative_value),
            expected_res)
