# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestQualityControl(TransactionCase):

    def setUp(self):
        super(TestQualityControl, self).setUp()
        self.picking_model = self.env['stock.picking']
        self.inspection_model = self.env['qc.inspection']
        self.qc_trigger_model = self.env['qc.trigger']
        self.picking_type_model = self.env['stock.picking.type']
        self.product = self.env.ref('product.product_product_4')
        self.partner1 = self.env.ref('base.res_partner_2')
        self.partner2 = self.env.ref('base.res_partner_4')
        self.test = self.env.ref('quality_control.qc_test_1')
        self.picking_type = self.env.ref('stock.picking_type_out')
        self.sequence = self.env.ref('stock.seq_type_picking_out')
        inspection_lines = (
            self.inspection_model._prepare_inspection_lines(self.test))
        self.inspection1 = self.inspection_model.create({
            'name': 'Test Inspection',
            'inspection_lines': inspection_lines,
        })
        self.trigger = self.qc_trigger_model.search(
            [('picking_type', '=', self.picking_type.id)])
        self.lot = self.env['stock.production.lot'].create({
            'name': 'Lot for tests',
            'product_id': self.product.id,
        })
        move_vals = {
            'name': self.product.name,
            'product_id': self.product.id,
            'product_uom': self.product.uom_id.id,
            'product_uom_qty': 2.0,
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
        for line in self.picking1.pack_operation_ids.filtered(
                lambda r: r.product_id == self.product):
            line.write({'lot_id': self.lot.id})

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
        inspection = self.picking1.qc_inspections[:1]
        self.assertEqual(inspection.qty, 2.0)
        self.assertEqual(inspection.test, self.test,
                         'Wrong test picked when creating inspection.')
        # Try in this context if onchange with an stock.pack.operation works
        inspection.qty = 5
        inspection.onchange_object_id()
        self.assertEqual(inspection.qty, 2.0)

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
        self.assertEqual(self.picking1.qc_inspections[:1].test, self.test,
                         'Wrong test picked when creating inspection.')

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
        self.assertEqual(self.picking1.qc_inspections[:1].test, self.test,
                         'Wrong test picked when creating inspection.')

    def test_inspection_create_for_product_partner(self):
        self.product.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
                'partners': [(6, 0, self.partner1.ids)],
            }
        )]
        self.picking1.do_transfer()
        self.assertEqual(self.picking1.created_inspections, 1,
                         'Only one inspection must be created')
        self.assertEqual(self.picking1.qc_inspections[:1].test, self.test,
                         'Wrong test picked when creating inspection.')

    def test_inspection_create_for_template_partner(self):
        self.product.product_tmpl_id.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
                'partners': [(6, 0, self.partner1.ids)],
            }
        )]
        self.picking1.do_transfer()
        self.assertEqual(self.picking1.created_inspections, 1,
                         'Only one inspection must be created')
        self.assertEqual(self.picking1.qc_inspections[:1].test, self.test,
                         'Wrong test picked when creating inspection.')

    def test_inspection_create_for_category_partner(self):
        self.product.categ_id.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
                'partners': [(6, 0, self.partner1.ids)],
            }
        )]
        self.picking1.do_transfer()
        self.assertEqual(self.picking1.created_inspections, 1,
                         'Only one inspection must be created')
        self.assertEqual(self.picking1.qc_inspections[:1].test, self.test,
                         'Wrong test picked when creating inspection.')

    def test_inspection_create_for_product_wrong_partner(self):
        self.product.qc_triggers = [(
            0, 0, {
                'trigger': self.trigger.id,
                'test': self.test.id,
                'partners': [(6, 0, self.partner2.ids)],
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
                'partners': [(6, 0, self.partner2.ids)],
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
                'partners': [(6, 0, self.partner2.ids)],
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
        self.assertEqual(self.picking1.qc_inspections[:1].test, self.test,
                         'Wrong test picked when creating inspection.')
        self.assertEqual(self.lot.created_inspections, 1,
                         'Only one inspection must be created')
        self.assertEqual(self.lot.qc_inspections[:1].test, self.test,
                         'Wrong test picked when creating inspection.')

    def test_picking_type(self):
        picking_type = self.picking_type_model.create({
            'name': 'Test Picking Type',
            'sequence_id': self.sequence.id,
            'code': 'outgoing',
        })
        trigger = self.qc_trigger_model.search(
            [('picking_type', '=', picking_type.id)])
        self.assertEqual(len(trigger), 1,
                         'One trigger must have been created.')
        self.assertEqual(trigger.name, picking_type.complete_name,
                         'Trigger name must match picking type name.')
        picking_type.write({
            'name': 'Test Name Change',
        })
        self.assertEqual(trigger.name, picking_type.complete_name,
                         'Trigger name must match picking type name.')

    def test_qc_inspection_picking(self):
        self.inspection1.write({
            'object_id': '%s,%d' % (self.picking1._model,
                                    self.picking1.id),
        })
        self.assertEquals(self.inspection1.picking,
                          self.picking1)

    def test_qc_inspection_stock_move(self):
        self.inspection1.write({
            'object_id': '%s,%d' % (self.picking1.move_lines[:1]._model,
                                    self.picking1.move_lines[:1].id),
        })
        self.inspection1.onchange_object_id()
        self.assertEquals(self.inspection1.picking,
                          self.picking1)
        self.assertEquals(self.inspection1.lot,
                          self.picking1.move_lines[:1].lot_ids[:1])
        self.assertEquals(self.inspection1.product,
                          self.picking1.move_lines[:1].product_id)
        self.assertEquals(self.inspection1.qty,
                          self.picking1.move_lines[:1].product_qty)
