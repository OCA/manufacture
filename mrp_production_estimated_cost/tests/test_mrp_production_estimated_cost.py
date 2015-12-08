# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza
# © 2015 Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests import common


class TestMrpProductionEstimatedCost(common.TransactionCase):
    def setUp(self):
        super(TestMrpProductionEstimatedCost, self).setUp()
        self.production = self.env.ref(
            'mrp_operations_extension.mrp_production_opeext')
        self.journal_materials = self.env.ref('mrp.analytic_journal_materials')
        self.journal_machines = self.env.ref('mrp.analytic_journal_machines')
        self.journal_operators = self.env.ref('mrp.analytic_journal_operators')

    def test_flow(self):
        self.production.action_compute()
        self.production.workcenter_lines[0].op_number = 1
        self.production.signal_workflow('button_confirm')
        self.production.force_production()
        self.assertTrue(self.production.analytic_line_ids.filtered(
            lambda x: x.journal_id == self.journal_materials))
        self.assertTrue(self.production.analytic_line_ids.filtered(
            lambda x: x.journal_id == self.journal_machines))
        self.assertTrue(self.production.analytic_line_ids.filtered(
            lambda x: x.journal_id == self.journal_operators))
        self.assertEqual(self.production.created_estimated_cost, 11)

    def test_show_action(self):
        action = self.production.action_show_estimated_costs
        self.assertTrue(action)
