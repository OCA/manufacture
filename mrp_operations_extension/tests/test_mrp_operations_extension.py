# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
import openerp.tests.common as common
from openerp import workflow


class TestMrpOperationsExtension(common.TransactionCase):

    def setUp(self):
        super(TestMrpOperationsExtension, self).setUp()
        self.production_model = self.env['mrp.production']
        self.work_order_produce_model = self.env['mrp.work.order.produce']
        self.produce_line_model = self.env['mrp.product.produce.line']
        self.production = self.production_model.browse(
            self.env.ref('mrp_operations_extension.mrp_production_opeext').id)
        self.production_case1 = self.production.copy()

    def test_confirm_production_operation_extension_case1(self):
        workflow.trg_validate(
            self.uid, 'mrp.production', self.production_case1.id,
            'button_confirm', self.cr)
        self.production_case1.force_production()
        for line in self.production_case1.workcenter_lines:
            workflow.trg_validate(self.uid, 'mrp.production.workcenter.line',
                                  line.id, 'button_start_working', self.cr)
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
            workflow.trg_validate(
                self.uid, 'mrp.production.workcenter.line', line.id,
                'button_done', self.cr)
            self.assertEqual(
                line.state, 'done',
                'Error work center line not in done state')
