# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestQualityControl(TransactionCase):

    def setUp(self):
        super(TestQualityControl, self).setUp()
        self.picking_model = self.env['stock.picking']
        self.operation_model = self.env['stock.pack.operation']
        self.transfer_details_model = self.env['stock.transfer_details']
        self.qc_trigger_model = self.env['qc.trigger']
        self.product = self.env.ref('product.product_product_4')
        self.partner1 = self.env.ref('base.res_partner_2')
        self.partner2 = self.env.ref('base.res_partner_4')
        self.test = self.env.ref('quality_control.qc_test_1')
        self.picking_type = self.env.ref('stock.picking_type_out')
        self.trigger = self.qc_trigger_model.search(
            [('picking_type', '=', self.picking_type.id)])
        move_vals = {
            'name': self.product.name,
            'product_id': self.product.id,
            'product_uom': self.product.uom_id.id,
            'location_id': self.picking_type.default_location_src_id.id,
            'location_dest_id': self.picking_type.default_location_dest_id.id,
        }
        self.picking1 = self.picking_model.create({
            'partner_id': self.partner1.id,
            'picking_type_id': self.picking_type.id,
            'move_lines': [(0, 0, move_vals)],
        })
        self.picking1.action_confirm()
        self.picking1.force_assign()
        self.picking1.do_prepare_partial()

    def test_inspection_create_for_product(self):
        self.product.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
            }
        )]
        self.picking1.do_transfer()
        self.assertEqual(self.picking1.created_inspections, 1,
                         'Only one inspection must be created')

    def test_inspection_create_for_template(self):
        self.product.product_tmpl_id.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
            }
        )]
        self.picking1.do_transfer()
        self.assertEqual(self.picking1.created_inspections, 1,
                         'Only one inspection must be created')

    def test_inspection_create_for_category(self):
        self.product.categ_id.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
            }
        )]
        self.picking1.do_transfer()
        self.assertEqual(self.picking1.created_inspections, 1,
                         'Only one inspection must be created')

    def test_inspection_create_for_product_partner(self):
        self.product.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
                'partners': [(6, 0, [self.partner1.id])],
            }
        )]
        self.picking1.do_transfer()
        self.assertEqual(self.picking1.created_inspections, 1,
                         'Only one inspection must be created')

    def test_inspection_create_for_template_partner(self):
        self.product.product_tmpl_id.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
                'partners': [(6, 0, [self.partner1.id])],
            }
        )]
        self.picking1.do_transfer()
        self.assertEqual(self.picking1.created_inspections, 1,
                         'Only one inspection must be created')

    def test_inspection_create_for_category_partner(self):
        self.product.categ_id.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
                'partners': [(6, 0, [self.partner1.id])],
            }
        )]
        self.picking1.do_transfer()
        self.assertEqual(self.picking1.created_inspections, 1,
                         'Only one inspection must be created')

    def test_inspection_create_for_product_wrong_partner(self):
        self.product.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
                'partners': [(6, 0, [self.partner2.id])],
            }
        )]
        self.picking1.do_transfer()
        self.assertEqual(self.picking1.created_inspections, 0,
                         'No inspection must be created')

    def test_inspection_create_for_template_wrong_partner(self):
        self.product.product_tmpl_id.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
                'partners': [(6, 0, [self.partner2.id])],
            }
        )]
        self.picking1.do_transfer()
        self.assertEqual(self.picking1.created_inspections, 0,
                         'No inspection must be created')

    def test_inspection_create_for_category_wrong_partner(self):
        self.product.categ_id.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
                'partners': [(6, 0, [self.partner2.id])],
            }
        )]
        self.picking1.do_transfer()
        self.assertEqual(self.picking1.created_inspections, 0,
                         'No inspection must be created')

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
        self.picking1.do_transfer()
        self.assertEqual(self.picking1.created_inspections, 1,
                         'Only one inspection must be created')
