# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestQualityControlMrp(TransactionCase):

    def setUp(self):
        super(TestQualityControlMrp, self).setUp()
        self.production_model = self.env['mrp.production']
        self.inspection_model = self.env['qc.inspection']
        self.qc_trigger_model = self.env['qc.trigger']
        self.product = self.env.ref('product.product_product_4')
        self.test = self.env.ref('quality_control.qc_test_1')
        self.trigger = self.env.ref('quality_control_mrp.qc_trigger_mrp')
        self.production1 = self.production_model.create({
            'product_id': self.product.id,
            'product_qty': 2.0,
            'product_uom': self.product.uom_id.id,
        })
        self.production1.action_confirm()
        self.production1.action_assign()
        inspection_lines = (
            self.inspection_model._prepare_inspection_lines(self.test))
        self.inspection1 = self.inspection_model.create({
            'name': 'Test Inspection',
            'inspection_lines': inspection_lines,
        })

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

    def test_inspection_with_partial_fabrication(self):
        self.product.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
            }
        )]
        self.production1.action_produce(
            self.production1.id, 1.0, 'consume_produce')
        self.assertEqual(self.production1.created_inspections, 1,
                         'Only one inspection must be created.')
        self.production1.action_produce(
            self.production1.id, 1.0, 'consume_produce')
        self.assertEqual(self.production1.created_inspections, 2,
                         'There must be only 2 inspections.')

    def test_qc_inspection_mo(self):
        self.inspection1.write({
            'object_id': '%s,%d' % (self.production1._model,
                                    self.production1.id),
        })
        self.assertEquals(self.inspection1.production,
                          self.production1)
