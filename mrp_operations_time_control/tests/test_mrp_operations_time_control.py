# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza
# © 2015 Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests import common
import time


class TestMrpOperationsTimeControl(common.TransactionCase):
    def setUp(self):
        super(TestMrpOperationsTimeControl, self).setUp()
        self.production = self.env.ref(
            'mrp_operations_extension.mrp_production_opeext')
        self.production.signal_workflow('button_confirm')
        self.production.force_production()
        self.workorder = self.production.workcenter_lines[0]

    def test_operations_time(self):
        self.assertFalse(self.workorder.operation_time_lines)
        self.workorder.action_start_working()
        self.assertTrue(self.workorder.operation_time_lines)
        time.sleep(1)
        self.workorder.action_pause()
        self.assertEqual(len(self.workorder.operation_time_lines), 1)
        self.assertTrue(self.workorder.operation_time_lines[0].uptime)
        self.workorder.action_resume()
        time.sleep(1)
        self.workorder.action_done()
        self.assertEqual(len(self.workorder.operation_time_lines), 2)
        self.assertTrue(self.workorder.operation_time_lines[1].uptime)
