# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase
from openerp import exceptions
from ..models.qc_trigger_line import\
    _filter_trigger_lines


class TestQualityControl(TransactionCase):

    def setUp(self):
        super(TestQualityControl, self).setUp()
        self.inspection_model = self.env['qc.inspection']
        self.category_model = self.env['qc.test.category']
        self.question_model = self.env['qc.test.question']
        self.wizard_model = self.env['qc.inspection.set.test']
        self.qc_trigger = self.env['qc.trigger'].create({
            'name': 'Test Trigger',
            'active': True,
        })
        self.test = self.env.ref('quality_control.qc_test_1')
        self.val_ok = self.env.ref('quality_control.qc_test_question_value_1')
        self.val_ko = self.env.ref('quality_control.qc_test_question_value_2')
        self.qn_question = self.env.ref('quality_control.qc_test_question_2')
        self.cat_generic = self.env.ref(
            'quality_control.qc_test_template_category_generic')
        self.product = self.env.ref('product.product_product_11')
        inspection_lines = (
            self.inspection_model._prepare_inspection_lines(self.test))
        self.inspection1 = self.inspection_model.create({
            'name': 'Test Inspection',
            'inspection_lines': inspection_lines,
        })
        self.wizard = self.wizard_model.with_context(
            active_id=self.inspection1.id).create({
                'test': self.test.id,
            })
        self.wizard.action_create_test()
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
        self.assertEquals(self.inspection1.state, 'success')
        self.inspection1.action_approve()
        self.assertEquals(self.inspection1.state, 'success')

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
        self.assertEquals(self.inspection1.state, 'waiting')
        self.inspection1.action_approve()
        self.assertEquals(self.inspection1.state, 'failed')

    def test_actions_errors(self):
        inspection2 = self.inspection1.copy()
        inspection2.action_draft()
        inspection2.write({'test': False})
        with self.assertRaises(exceptions.Warning):
            inspection2.action_todo()
        inspection3 = self.inspection1.copy()
        inspection3.write({
            'inspection_lines':
            self.inspection_model._prepare_inspection_lines(inspection3.test)
        })
        for line in inspection3.inspection_lines:
            if line.question_type == 'quantitative':
                line.quantitative_value = 15.0
        with self.assertRaises(exceptions.Warning):
            inspection3.action_confirm()
        inspection4 = self.inspection1.copy()
        inspection4.write({
            'inspection_lines':
            self.inspection_model._prepare_inspection_lines(inspection4.test)
        })
        for line in inspection4.inspection_lines:
            if line.question_type == 'quantitative':
                line.write({
                    'uom_id': False,
                    'quantitative_value': 15.0,
                })
            elif line.question_type == 'qualitative':
                line.qualitative_value = self.val_ok
        with self.assertRaises(exceptions.Warning):
            inspection4.action_confirm()

    def test_categories(self):
        category1 = self.category_model.create({
            'name': 'Category ONE',
        })
        category2 = self.category_model.create({
            'name': 'Category TWO',
            'parent_id': category1.id,
        })
        self.assertEquals(
            category2.complete_name,
            '%s / %s' % (category1.name, category2.name),
            'Something went wrong when computing complete name')
        with self.assertRaises(exceptions.ValidationError):
            category1.parent_id = category2.id

    def test_get_qc_trigger_product(self):
        self.test.write({
            'fill_correct_values': True,
        })
        trigger_lines = set()
        self.product.write({
            'qc_triggers': [(0, 0, {'trigger': self.qc_trigger.id,
                                    'test': self.test.id})],
        })
        self.product.product_tmpl_id.write({
            'qc_triggers': [(0, 0, {'trigger': self.qc_trigger.id,
                                    'test': self.test.id})],
        })
        self.product.categ_id.write({
            'qc_triggers': [(0, 0, {'trigger': self.qc_trigger.id,
                                    'test': self.test.id})],
        })
        for model in ['qc.trigger.product_category_line',
                      'qc.trigger.product_template_line',
                      'qc.trigger.product_line']:
            trigger_lines = trigger_lines.union(
                self.env[model].get_trigger_line_for_product(
                    self.qc_trigger, self.product))
        self.assertEquals(len(trigger_lines), 3)
        filtered_trigger_lines = _filter_trigger_lines(trigger_lines)
        self.assertEquals(len(filtered_trigger_lines), 1)
        for trigger_line in filtered_trigger_lines:
            inspection = self.inspection_model._make_inspection(
                self.product, trigger_line)
            self.assertEquals(inspection.state, 'ready')
            self.assertTrue(inspection.auto_generated)
            self.assertEquals(inspection.test, self.test)
            for line in inspection.inspection_lines:
                if line.question_type == 'qualitative':
                    self.assertEquals(line.qualitative_value, self.val_ok)
                elif line.question_type == 'quantitative':
                    self.assertEquals(
                        round(line.quantitative_value, 2), round((
                            self.qn_question.min_value +
                            self.qn_question.max_value) * 0.5, 2))

    def test_qc_inspection_not_draft_unlink(self):
        with self.assertRaises(exceptions.Warning):
            self.inspection1.unlink()
        inspection2 = self.inspection1.copy()
        inspection2.action_cancel()
        self.assertEquals(inspection2.state, 'canceled')
        inspection2.action_draft()
        self.assertEquals(inspection2.state, 'draft')
        inspection2.unlink()

    def test_qc_inspection_auto_generate_unlink(self):
        inspection2 = self.inspection1.copy()
        inspection2.write({
            'auto_generated': True,
        })
        with self.assertRaises(exceptions.Warning):
            inspection2.unlink()

    def test_qc_inspection_product(self):
        self.inspection1.write({
            'object_id': '%s,%d' % (self.product._model, self.product.id),
        })
        self.assertEquals(self.inspection1.product,
                          self.product)

    def test_qc_test_question_constraints(self):
        with self.assertRaises(exceptions.ValidationError):
            self.question_model.create({
                'name': 'Quantitative Question',
                'type': 'quantitative',
                'min_value': 1.0,
                'max_value': 0.0,
            })
        with self.assertRaises(exceptions.ValidationError):
            self.question_model.create({
                'name': 'Qualitative Question',
                'type': 'qualitative',
                'ql_values': [(0, 0, {'name': 'Qualitative answer',
                                      'ok': False})],
            })
