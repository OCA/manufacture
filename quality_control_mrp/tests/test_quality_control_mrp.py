# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestQualityControlMrp(TransactionCase):

    def setUp(self):
        super(TestQualityControlMrp, self).setUp()
        self.production_model = self.env['mrp.production']
        self.qc_trigger_model = self.env['qc.trigger']
        self.product = self.env.ref('product.product_product_4')
        self.test = self.env.ref('quality_control.qc_test_1')
        self.trigger = self.env.ref('quality_control_mrp.qc_trigger_mrp')
        self.production1 = self.production_model.create({
            'product_id': self.product.id,
            'product_uom': self.product.uom_id.id,
        })
        self.production1.action_confirm()
        self.production1.action_assign()

    def test_inspection_create_for_product(self):
        self.product.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
            }
        )]
        self.production1.action_produce(
            self.production1.id, self.production1.product_qty,
            'consume_produce')
        self.assertEqual(self.production1.created_inspections, 1,
                         'Only one inspection must be created')

    def test_inspection_create_for_template(self):
        self.product.product_tmpl_id.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
            }
        )]
        self.production1.action_produce(
            self.production1.id, self.production1.product_qty,
            'consume_produce')
        self.assertEqual(self.production1.created_inspections, 1,
                         'Only one inspection must be created')

    def test_inspection_create_for_category(self):
        self.product.categ_id.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
            }
        )]
        self.production1.action_produce(
            self.production1.id, self.production1.product_qty,
            'consume_produce')
        self.assertEqual(self.production1.created_inspections, 1,
                         'Only one inspection must be created')

    def test_inspection_create_only_one(self):
        self.product.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
            }
        )]
        self.product.categ_id.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
            }
        )]
        self.production1.action_produce(
            self.production1.id, self.production1.product_qty,
            'consume_produce')
        self.assertEqual(self.production1.created_inspections, 1,
                         'Only one inspection must be created')
