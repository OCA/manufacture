# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza
# © 2015 Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests import common
import time


class TestMrpProductionRealCost(common.TransactionCase):
    def setUp(self):
        super(TestMrpProductionRealCost, self).setUp()
        self.production = self.env.ref(
            'mrp_operations_extension.mrp_production_opeext')
        self.production.signal_workflow('button_confirm')
        self.production.force_production()

    def test_flow(self):
        line = self.production.workcenter_lines[1]
        line.pre_cost = 10
        line.post_cost = 20
        line.signal_workflow('button_start_working')
        self.assertEqual(len(self.production.analytic_line_ids), 1)
        time.sleep(1)
        line.signal_workflow('button_pause')
        self.assertEqual(len(self.production.analytic_line_ids), 2)
        line.signal_workflow('button_resume')
        time.sleep(1)
        line.signal_workflow('button_done')
        self.assertEqual(len(self.production.analytic_line_ids), 4)
        self.production.analytic_line_ids[:1].amount = -10
        self.assertTrue(self.production.real_cost)

    def test_produce(self):
        # Set an impossible price to see if it changes
        initial_price = 999999999
        self.production.product_id.standard_price = initial_price
        self.production.product_id.cost_method = 'average'
        self.production.action_produce(
            self.production.id, self.production.product_qty, 'consume_produce')
        self.assertEqual(len(self.production.analytic_line_ids), 4)
        self.assertNotEqual(
            initial_price, self.production.product_id.standard_price)
