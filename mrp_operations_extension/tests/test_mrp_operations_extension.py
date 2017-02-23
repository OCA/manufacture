# -*- coding: utf-8 -*-
# © 2015 Avanzosc
# © 2015 Pedro M. Baeza
# © 2015 Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp.exceptions import ValidationError, Warning as UserError


class TestMrpOperationsExtension(common.TransactionCase):
    def setUp(self):
        super(TestMrpOperationsExtension, self).setUp()
        self.workcenter = self.env['mrp.workcenter'].create(
            {'name': 'Test work center',
             'op_number': 1,
             'capacity_per_cycle': 5,
             'time_cycle': 1.0}
        )
        self.operation = self.env['mrp.routing.operation'].create(
            {'name': 'Test operation',
             'op_number': 2,
             'workcenters': [(6, 0, self.workcenter.ids)]})
        self.routing = self.env['mrp.routing'].create(
            {'name': 'Test routing'})
        self.routing_workcenter = self.env['mrp.routing.workcenter'].create(
            {
                'name': 'Test routing line',
                'do_production': True,
                'workcenter_id': self.workcenter.id,
                'routing_id': self.routing.id,
            })
        self.operation_workcenter = (
            self.env['mrp.operation.workcenter'].create(
                {
                    'workcenter': self.workcenter.id,
                    'routing_workcenter': self.routing_workcenter.id,
                    'default': True,
                }))
        self.production_model = self.env['mrp.production']
        self.work_order_produce_model = self.env['mrp.work.order.produce']
        self.produce_line_model = self.env['mrp.product.produce.line']
        self.production = self.env.ref(
            'mrp_operations_extension.mrp_production_opeext')
        self.workcenter_line_finish = self.env['workcenter.line.finish']

    def test_check_do_production_mrp_routing(self):
        # None of the workcenter lines have the check marked
        with self.assertRaises(ValidationError):
            self.routing.workcenter_lines = [
                (1, self.routing_workcenter.id, {'do_production': False})]

    def test_check_do_production_mrp_routing_2(self):
        # Two workcenter lines have the check marked
        with self.assertRaises(ValidationError):
            self.routing.workcenter_lines = [(0, 0, {
                'name': 'Other test routing line',
                'do_production': True,
                'workcenter_id': self.workcenter.id,
            })]

    def test_check_default_mrp_routing_workcenter(self):
        # None of the operation workcenters have the check marked
        with self.assertRaises(ValidationError):
            self.routing_workcenter.op_wc_lines = [
                (1, self.operation_workcenter.id, {'default': False})]

    def test_check_default_mrp_routing_workcenter_2(self):
        # Two operation workcenters have the check marked
        with self.assertRaises(ValidationError):
            self.routing_workcenter.op_wc_lines = [(0, 0, {
                'default': True,
                'routing_workcenter': self.routing_workcenter.id,
                'workcenter': self.workcenter.id,
            })]

    def test_onchange_operation_mrp_routing_workcenter(self):
        with self.env.do_in_onchange():
            record = self.env['mrp.routing.workcenter'].new()
            record.operation = self.operation.id
            record.onchange_operation()
            self.assertEqual(record.name, self.operation.name)
            self.assertEqual(len(record.op_wc_lines), 1)
            self.assertEqual(record.op_wc_lines[0].op_number, 2)

    def test_onchange_workcenter_mrp_operation_workcenter(self):
        with self.env.do_in_onchange():
            record = self.env['mrp.operation.workcenter'].new()
            record.workcenter = self.workcenter.id
            record.onchange_workcenter()
            self.assertEqual(
                record.capacity_per_cycle, self.workcenter.capacity_per_cycle)
            self.assertEqual(
                record.time_efficiency, self.workcenter.time_efficiency)
            self.assertEqual(record.op_number, self.workcenter.op_number)

    def test_onchange_operators_mrp_workcenter(self):
        user = self.env['res.users'].create({
            'name': 'Test user',
            'login': 'test',
        })
        cost_product = self.env['product.product'].create(
            {'name': 'Cost product',
             'standard_price': 15.0})
        self.env['hr.employee'].create({
            'name': 'Test employee',
            'user_id': user.id,
            'product_id': cost_product.id})
        with self.env.do_in_onchange():
            record = self.env['mrp.workcenter'].new()
            record.operators = [(6, 0, user.ids)]
            record.onchange_operators()
            self.assertEqual(record.op_number, 1)
            self.assertEqual(record.op_avg_cost, 15.0)

    def test_onchange_routing_mrp_bom(self):
        with self.env.do_in_onchange():
            record = self.env['mrp.bom'].new()
            record.bom_line_ids = self.env['mrp.bom.line'].new()
            record.routing_id = self.routing.id
            res = record.onchange_routing_id()
            self.assertTrue(res['warning'])

    def test_start_workorder_without_material(self):
        self.production.signal_workflow('button_confirm')
        workorder = self.production.workcenter_lines[0]
        with self.assertRaises(UserError):
            # Missing materials to start the production
            workorder.action_start_working()
        # In this case it should work
        workorder.action_assign()
        workorder.force_assign()
        workorder.action_start_working()

    def test_start_second_workorder(self):
        self.production.signal_workflow('button_confirm')
        self.production.workcenter_lines[1].routing_wc_line.\
            previous_operations_finished = True
        with self.assertRaises(UserError):
            # Previous operations not finished
            self.production.workcenter_lines[1].action_start_working()

    def test_create_workcenter_minor_date(self):
        date_planned = '1900-01-01 00:00:00'
        self.env['mrp.production.workcenter.line'].create(
            {'name': 'Test',
             'date_planned': date_planned,
             'workcenter_id': self.workcenter.id,
             'production_id': self.production.id})
        self.assertEqual(self.production.date_planned, date_planned)

    def test_confirm_production_without_do_production_flag(self):
        self.production.action_compute()
        self.production.workcenter_lines.write({'do_production': False})
        with self.assertRaises(UserError):
            # At least one work order must have checked 'Produce here'
            self.production.action_confirm()

    def test_confirm_production_operation_extension_case1(self):
        self.assertEqual(self.production.state, 'draft')
        self.production.signal_workflow('button_confirm')
        self.assertFalse(self.production.workcenter_lines[0].is_material_ready)
        self.production.force_production()
        for line in self.production.workcenter_lines:
            self.assertTrue(line.is_material_ready)
            self.assertEqual(len(line.possible_workcenters),
                             len(line.routing_wc_line.op_wc_lines))
            line.signal_workflow('button_start_working')
            self.assertEqual(
                line.state, 'startworking',
                'Error work center line not in start working state')
            consume = self.work_order_produce_model.with_context(
                active_ids=[line.id], active_id=line.id).create({})
            result = consume.with_context(
                active_ids=[line.id], active_id=line.id).on_change_qty(
                consume.product_qty, [])
            if 'value' in result:
                if ('consume_lines' in result['value'] and
                        result['value']['consume_lines']):
                    for cl in result['value']['consume_lines']:
                        consu_vals = cl[2]
                        consu_vals['work_produce_id'] = consume.id
                        self.produce_line_model.create(consu_vals)
            if not consume.final_product:
                consume.with_context(active_id=line.id).do_consume()
            else:
                consume.with_context(active_id=line.id).do_consume_produce()
            line.signal_workflow('button_done')
            self.assertEqual(
                line.state, 'done',
                'Error work center line not in done state')

    def test_operation_button_done(self):
        self.production.signal_workflow('button_confirm')
        workorder = self.production.workcenter_lines[0]
        workorder.action_assign()
        workorder.force_assign()
        workorder.signal_workflow('button_start_working')
        res = workorder.button_done()
        if res:  # check make_them_done
            lines2move = len(workorder.move_lines.filtered(
                lambda x: x.state not in ('done')))
            self.workcenter_line_finish.with_context(
                active_id=workorder.id,
                active_model='mrp.production.workcenter.line').make_them_done()
            lines_done = len(workorder.move_lines.filtered(
                lambda x: x.state in ('done')))
            self.assertEqual(lines2move, lines_done,
                             'Error work order moves quantity do not match')
            self.assertEqual(workorder.state, 'done',
                             'Error work center line not in done state')
        workorder1 = self.production.workcenter_lines[1]
        workorder1.signal_workflow('button_start_working')
        res1 = workorder1.button_done()
        self.assertFalse(res1, 'Error there are pending movements')
        workorder2 = self.production.workcenter_lines[2]
        workorder2.action_assign()
        workorder2.force_assign()
        workorder2.signal_workflow('button_start_working')
        res2 = workorder2.button_done()
        if res2:  # check cancel_all
            lines2move2 = len(workorder2.move_lines.filtered(
                lambda x: x.state not in ('cancel')))
            self.workcenter_line_finish.with_context(
                active_id=workorder2.id,
                active_model='mrp.production.workcenter.line').cancel_all()
            lines_cancel = len(workorder2.move_lines.filtered(
                lambda x: x.state in ('cancel')))
            self.assertEqual(lines2move2, lines_cancel,
                             'Error work order moves quantity do not match')
            self.assertEqual(workorder2.state, 'done',
                             'Error work center line not in done state')

    def test_param_config(self):
        wiz_config_obj = self.env['mrp.config.settings']
        param_obj = self.env['ir.config_parameter']
        rec = param_obj.search([('key', '=', 'cycle.by.bom')])
        self.assertEqual(rec.value, 'True', 'Error cycle.by.bom is not marked')
        rec.unlink()
        record = wiz_config_obj.new()
        record.set_parameter_cycle_bom()
        rec = param_obj.search([('key', '=', 'cycle.by.bom')])
        self.assertEqual(rec.value, 'False', 'Error cycle.by.bom is marked')
        record.cycle_by_bom = True
        record.set_parameter_cycle_bom()
        rec = param_obj.search([('key', '=', 'cycle.by.bom')])
        self.assertEqual(rec.value, 'True', 'Error cycle.by.bom not marked')
