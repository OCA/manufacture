# -*- coding: utf-8 -*-
# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from datetime import datetime


class TestQualityControl(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestQualityControl, self).setUp(*args, **kwargs)

        self.obj_inspection = self.env["qc.inspection"]
        self.obj_wizard = self.env["qc.inspection.set.test"]

        self.inspection_test = self.env.ref(
            "quality_control.qc_test_1")

        self.val_ok = self.env.ref(
            "quality_control.qc_test_question_value_1")
        self.val_ko = self.env.ref(
            "quality_control.qc_test_question_value_2")

        self.inspection_data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def test_1(self):
        inspection = self.obj_inspection.create(
            self.inspection_data)
        wizard = self.obj_wizard.with_context(
            active_id=inspection.id).create({
                "test": self.inspection_test.id})
        wizard.action_create_test()

        # test should be filled
        self.assertTrue(
            inspection.test)

        # Inspection line number should be equal with test
        # inspection line.
        self.assertEqual(
            len(inspection.inspection_lines),
            len(self.inspection_test.test_lines))

        # answer with valid valud
        for line in inspection.inspection_lines:
            if line.question_type == 'qualitative':
                line.qualitative_value = self.val_ko
            if line.question_type == 'quantitative':
                line.quantitative_value = 15.0

        inspection.action_confirm()
        self.assertEqual(
            inspection.state,
            "waiting")

        # approve
        inspection.action_approve()

        # inspection should be failed
        self.assertEqual(
            inspection.state,
            "failed")

    def test_2(self):
        inspection = self.obj_inspection.create(
            self.inspection_data)
        wizard = self.obj_wizard.with_context(
            active_id=inspection.id).create({
                "test": self.inspection_test.id})
        wizard.action_create_test()

        # test should be filled
        self.assertTrue(
            inspection.test)

        # Inspection line number should be equal with test
        # inspection line.
        self.assertEqual(
            len(inspection.inspection_lines),
            len(self.inspection_test.test_lines))

        # answer with valid valud
        for line in inspection.inspection_lines:
            if line.question_type == 'qualitative':
                line.qualitative_value = self.val_ko
            if line.question_type == 'quantitative':
                line.quantitative_value = 15.0

        inspection.action_confirm()
        self.assertEqual(
            inspection.state,
            "waiting")

        # force valid
        inspection.force_valid = True

        # approve
        inspection.action_approve()

        # inspection should be success
        self.assertEqual(
            inspection.state,
            "success")

    def test_3(self):
        inspection = self.obj_inspection.create(
            self.inspection_data)
        wizard = self.obj_wizard.with_context(
            active_id=inspection.id).create({
                "test": self.inspection_test.id})
        wizard.action_create_test()

        # test should be filled
        self.assertTrue(
            inspection.test)

        # Inspection line number should be equal with test
        # inspection line.
        self.assertEqual(
            len(inspection.inspection_lines),
            len(self.inspection_test.test_lines))

        # answer with valid valud
        for line in inspection.inspection_lines:
            if line.question_type == 'qualitative':
                line.qualitative_value = self.val_ko
            if line.question_type == 'quantitative':
                line.quantitative_value = 15.0

        # force valid
        inspection.force_valid = True

        inspection.action_confirm()
        self.assertEqual(
            inspection.state,
            "success")

        # approve
        inspection.action_approve()

        # inspection should be success
        self.assertEqual(
            inspection.state,
            "success")
