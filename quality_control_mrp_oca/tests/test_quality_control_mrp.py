# -*- coding: utf-8 -*-
# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestQualityControlMrp(TransactionCase):

    def setUp(self):
        super(TestQualityControlMrp, self).setUp()
        self.production_model = self.env['mrp.production']
        self.inspection_model = self.env['qc.inspection']
        self.qc_trigger_model = self.env['qc.trigger']
        self.product = self.env.ref('mrp.product_product_computer_desk')
        self.test = self.env.ref('quality_control.qc_test_1')
        self.trigger = self.env.ref('quality_control_mrp.qc_trigger_mrp')
        self.bom = self.env['mrp.bom']._bom_find(product=self.product)
        self.production1 = self.production_model.create({
            'product_id': self.product.id,
            'product_qty': 2.0,
            'product_uom_id': self.product.uom_id.id,
            'bom_id': self.bom.id
        })
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
        produce_wizard = self.env['mrp.product.produce'].with_context({
            'active_id': self.production1.id,
            'active_ids': [self.production1.id],
        }).create({
            'product_qty': self.production1.product_qty
        })
        produce_wizard.do_produce()
        self.production1.post_inventory()
        self.assertEqual(self.production1.created_inspections, 1,
                         'Only one inspection must be created')

    def test_inspection_create_for_template(self):
        self.product.product_tmpl_id.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
            }
        )]
        produce_wizard = self.env['mrp.product.produce'].with_context({
            'active_id': self.production1.id,
            'active_ids': [self.production1.id]
        }).create({
            'product_qty': self.production1.product_qty
        })
        produce_wizard.do_produce()
        self.production1.post_inventory()
        self.assertEqual(self.production1.created_inspections, 1,
                         'Only one inspection must be created')

    def test_inspection_create_for_category(self):
        self.product.categ_id.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
            }
        )]
        produce_wizard = self.env['mrp.product.produce'].with_context({
            'active_id': self.production1.id,
            'active_ids': [self.production1.id],
        }).create({
            'product_qty': self.production1.product_qty
        })
        produce_wizard.do_produce()
        self.production1.post_inventory()
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
        produce_wizard = self.env['mrp.product.produce'].with_context({
            'active_id': self.production1.id,
            'active_ids': [self.production1.id]
        }).create({
            'product_qty': self.production1.product_qty
        })
        produce_wizard.do_produce()
        self.production1.post_inventory()
        self.assertEqual(self.production1.created_inspections, 1,
                         'Only one inspection must be created')

    def test_inspection_with_partial_fabrication(self):
        self.product.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
            }
        )]
        produce_wizard = self.env['mrp.product.produce'].with_context({
            'active_id': self.production1.id,
            'active_ids': [self.production1.id],
        }).create({
            'product_qty': 1.0
        })
        produce_wizard.do_produce()
        self.production1.post_inventory()
        self.assertEqual(self.production1.created_inspections, 1,
                         'Only one inspection must be created.')
        produce_wizard = self.env['mrp.product.produce'].with_context({
            'active_id': self.production1.id,
            'active_ids': [self.production1.id],
        }).create({
            'product_qty': 1.0
        })
        produce_wizard.do_produce()
        self.production1.post_inventory()
        self.assertEqual(self.production1.created_inspections, 2,
                         'There must be only 2 inspections.')

    def test_qc_inspection_mo(self):
        self.inspection1.write({
            'object_id': '%s,%d' % (self.production1._name,
                                    self.production1.id),
        })
        self.assertEquals(self.inspection1.production,
                          self.production1)
