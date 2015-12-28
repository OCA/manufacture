# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import time
import openerp.tests.common as common
from openerp import fields


class TestMrpProject(common.TransactionCase):
    def setUp(self):
        super(TestMrpProject, self).setUp()
        self.product = self.env['product.product'].create({'name': 'Test'})
        self.bom = self.env['mrp.bom'].create(
            {
                'product_id': self.product.id,
                'product_tmpl_id': self.product.product_tmpl_id.id,
            })
        self.production = self.env['mrp.production'].create(
            {
                'product_id': self.product.id,
                'product_uom': self.env.ref('product.product_uom_unit').id,
                'bom_id': self.bom.id,
            })
        self.task = self.env['project.task'].create({
            'name': "Test",
            'user_id': self.env.uid,
        })

    def test_project_full(self):
        self.assertFalse(self.production.project_id)
        self.production.signal_workflow('button_confirm')
        self.assertTrue(self.production.project_id)
        self.assertEqual(self.production.project_id.production_count, 1)
        self.production.force_production()
        # start the MO (and this starts the first WO)
        self.assertFalse(self.production.project_id.task_ids)
        self.production.signal_workflow('button_produce')
        self.assertEqual(len(self.production.project_id.task_ids), 1)
        # Remove production to see if the project is removed
        project = self.production.project_id
        self.production.signal_workflow('button_cancel')
        self.production.unlink()
        self.assertFalse(project.exists())

    def test_preservation_project_with_works(self):
        self.production.signal_workflow('button_confirm')
        self.production.force_production()
        self.production.signal_workflow('button_produce')
        work = self.env['project.task.work'].create(
            {'task_id': self.production.project_id.task_ids[0].id,
             'name': 'Test work',
             'user_id': self.env.user.id,
             'hours': 1.0})
        # Remove production to see if the project is removed
        project = self.production.project_id
        self.production.signal_workflow('button_cancel')
        self.production.unlink()
        self.assertTrue(project.exists())
        self.assertTrue(work.exists())

    def test_task_name(self):
        self.assertEqual(
            self.task.with_context(name_show_user=True).name_get()[0][1],
            "[%s] Test" % self.env.user.name)

    def test_onchange_task(self):
        res = self.env['project.task.work'].onchange_task_id(self.task.id)
        self.assertEqual(res['value']['user_id'], self.task.user_id.id)

    def test_button_end_work(self):
        work = self.env['project.task.work'].create(
            {'task_id': self.task.id,
             'name': 'Test',
             'user_id': self.env.uid,
             'hours': 0,
             'date': fields.Datetime.now()})
        time.sleep(1)
        work.button_end_work()
        self.assertNotEqual(work.hours, 0.0)
