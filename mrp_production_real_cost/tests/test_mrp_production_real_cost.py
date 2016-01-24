# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza
# © 2015 Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests import common
from openerp import fields
from datetime import timedelta


class TestMrpProductionRealCost(common.TransactionCase):
    def setUp(self):
        super(TestMrpProductionRealCost, self).setUp()
        self.production = self.env.ref(
            'mrp_operations_extension.mrp_production_opeext')
        self.production.signal_workflow('button_confirm')
        self.production.force_production()
        # start date will be used in order to force a long machine uptime
        self.start_date = (
            fields.Datetime.from_string(fields.Datetime.now()) -
            timedelta(hours=1))

    def test_flow(self):
        line = self.production.workcenter_lines[1]
        line.pre_cost = 10
        line.post_cost = 20
        line.signal_workflow('button_start_working')
        line.operation_time_lines[-1].start_date = (
            self.start_date - timedelta(hours=1))
        analytic_line = self.production.analytic_line_ids.filtered('amount')
        # This should have the pre-operation cost
        self.assertEqual(len(analytic_line), 1)
        line.signal_workflow('button_pause')
        analytic_lines = self.production.analytic_line_ids.filtered('amount')
        # This should have the pre-operation cost and uptime line
        self.assertEqual(len(analytic_lines), 2)
        prev_amount = analytic_lines[-1].amount
        line.signal_workflow('button_resume')
        line.operation_time_lines[-1].start_date = (
            self.start_date - timedelta(hours=2))
        line.signal_workflow('button_done')
        analytic_lines = self.production.analytic_line_ids.filtered('amount')
        # This should have the pre- cost, cycle cost, uptime line and
        # post- cost
        self.assertEqual(len(analytic_lines), 4)
        self.assertNotEqual(analytic_lines[-1].amount, prev_amount)
        prev_amount = analytic_lines[-1].amount
        # Change manually an uptime to see if costs change
        line.operation_time_lines[-1].end_date = (
            self.start_date + (timedelta(hours=3)))
        analytic_lines = self.production.analytic_line_ids.filtered('amount')
        self.assertNotEqual(analytic_lines[-1].amount, prev_amount)
        # Change analytic entries to see if production real_cost field changes
        self.production.analytic_line_ids[:1].amount = -10
        self.assertTrue(self.production.real_cost)

    def test_produce(self):
        # Set an impossible price to see if it changes
        initial_price = 999999999
        self.production.product_id.standard_price = initial_price
        self.production.product_id.cost_method = 'average'
        for line in self.production.workcenter_lines:
            line.signal_workflow('button_start_working')
            line.operation_time_lines[-1].start_date = self.start_date
        self.production.action_produce(
            self.production.id, self.production.product_qty, 'consume_produce')
        # This should have 2 materials and 2 workorders each with cycle and
        # uptime cost
        self.assertEqual(
            len(self.production.analytic_line_ids.filtered('amount')), 6)
        self.assertNotEqual(
            initial_price, self.production.product_id.standard_price)

    def test_onchange_lines_default(self):
        workcenter0 = self.browse_ref('mrp.mrp_workcenter_0')
        routing = self.env['mrp.routing.workcenter'].new({
            'name': 'Test Routing',
            'op_wc_lines': [(0, 0, {
                'default': True, 'workcenter': workcenter0.id})],
        })
        routing.onchange_lines_default()
        self.assertEqual(routing.workcenter_id, workcenter0)
        self.assertEqual(routing.cycle_nbr, workcenter0.capacity_per_cycle)
        self.assertEqual(routing.hour_nbr, workcenter0.time_cycle)
