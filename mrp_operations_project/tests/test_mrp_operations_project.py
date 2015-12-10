# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.mrp_project.tests import test_mrp_project


class TestMrpOperationsProject(test_mrp_project.TestMrpProject):
    def setUp(self):
        super(TestMrpOperationsProject, self).setUp()
        self.workcenter = self.env['mrp.workcenter'].create(
            {'name': 'Test work center'})
        self.routing = self.env['mrp.routing'].create(
            {
                'name': 'Test routing',
                'workcenter_lines': [
                    (0, 0, {'name': 'Test workcenter line',
                            'do_production': True,
                            'workcenter_id': self.workcenter.id})],
            })
        self.production.routing_id = self.routing.id

    def test_workcenter_tasks(self):
        self.workcenter.op_number = 1
        self.production.signal_workflow('button_confirm')
        self.production.force_production()
        # start the MO (and this starts the first WO)
        self.assertFalse(self.production.project_id.task_ids)
        self.production.signal_workflow('button_produce')
        self.assertEqual(len(self.production.workcenter_lines[0].task_m2m), 1)
        self.assertEqual(len(self.production.project_id.task_ids), 2)

    def test_project_full(self):
        """Don't repeat this test."""
        pass

    def test_preservation_project_with_works(self):
        """Don't repeat this test."""
        pass

    def test_onchange_task(self):
        """Don't repeat this test."""
        pass

    def test_button_end_work(self):
        """Don't repeat this test."""
        pass
