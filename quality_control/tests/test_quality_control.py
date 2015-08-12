# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestQualityControl(TransactionCase):

    def setUp(self):
        super(TestQualityControl, self).setUp()
        self.inspection_model = self.env['qc.inspection']
        self.test = self.env.ref('quality_control.qc_test_1')
        self.val_ok = self.env.ref('quality_control.qc_test_question_value_1')
        self.val_ko = self.env.ref('quality_control.qc_test_question_value_2')
        inspection_lines = (
            self.inspection_model._prepare_inspection_lines(self.test))
        self.inspection1 = self.inspection_model.create({
            'name': 'Test Inspection',
            'test': self.test.id,
            'inspection_lines': inspection_lines,
        })
        self.inspection1.action_todo()

    def test_inspection_correct(self):
        for line in self.inspection1.inspection_lines:
            if line.question_type == 'qualitative':
                line.qualitative_value = self.val_ok
            if line.question_type == 'quantitative':
                line.quantitative_value = 5.0
        self.inspection1.action_confirm()
        for line in self.inspection1.inspection_lines:
            self.assertTrue(
                line.success,
                'Incorrect state in inspection line %s' % line.name)
        self.assertTrue(
            self.inspection1.success,
            'Incorrect state in inspection %s' % self.inspection1.name)

    def test_inspection_incorrect(self):
        for line in self.inspection1.inspection_lines:
            if line.question_type == 'qualitative':
                line.qualitative_value = self.val_ko
            if line.question_type == 'quantitative':
                line.quantitative_value = 15.0
        self.inspection1.action_confirm()
        for line in self.inspection1.inspection_lines:
            self.assertFalse(
                line.success,
                'Incorrect state in inspection line %s' % line.name)
        self.assertFalse(
            self.inspection1.success,
            'Incorrect state in inspection %s' % self.inspection1.name)
