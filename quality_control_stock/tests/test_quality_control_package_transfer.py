# -*- coding: utf-8 -*-
# © 2016 Andhitia Rama (OpenSynergy Indonesia)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestQualityControlPackage(TransactionCase):

    def setUp(self):
        super(TestQualityControlPackage, self).setUp()
        self.picking_obj = self.env['stock.picking']
        self.inspection_obj = self.env['qc.inspection']
        self.qc_trigger_obj = self.env['qc.trigger']
        self.picking_type_obj = self.env['stock.picking.type']
        self.transfer_obj = self.env['stock.transfer_details']
        self.transfer_detail_obj = self.env['stock.transfer_details_items']
        self.qc_product_trg = self.env['qc.trigger.product_line']

        self.product = self.env.ref('product.product_product_4')
        self.test = self.env.ref('quality_control.qc_test_1')
        self.receipt_type = self.env.ref('stock.picking_type_in')
        self.internal_type = self.env.ref('stock.picking_type_internal')
        self.location_stock = self.env.ref('stock.stock_location_stock')
        self.location_shelf2 = self.env.ref('stock.stock_location_14')
        self.location_sup = self.env.ref('stock.stock_location_suppliers')
        self.trigger = self.qc_trigger_obj.search(
            [('picking_type', '=', self.internal_type.id)])

        move_vals = {
            'name': self.product.name,
            'product_id': self.product.id,
            'product_uom': self.product.uom_id.id,
            'product_uom_qty': 2.0,
            'location_id': self.location_sup.id,
            'location_dest_id': self.location_stock.id,
        }
        self.picking1 = self.picking_obj.create({
            'picking_type_id': self.receipt_type.id,
            'move_lines': [(0, 0, move_vals)],
        })
        move_vals2 = {
            'name': self.product.name,
            'product_id': self.product.id,
            'product_uom': self.product.uom_id.id,
            'product_uom_qty': 2.0,
            'location_id': self.location_stock.id,
            'location_dest_id': self.location_shelf2.id,
        }
        self.picking2 = self.picking_obj.create({
            'picking_type_id': self.internal_type.id,
            'move_lines': [(0, 0, move_vals2)],
        })
        qc_trigger_vals = {
            'trigger': self.trigger.id,
            'test': self.test.id,
            'product': self.product.id,
        }
        self.qc_product_trg.create(qc_trigger_vals)

    def test_1(self):
        self.picking1.signal_workflow('action_confirm')
        self.picking1.action_assign()
        wzd_view = self.picking1.do_enter_transfer_details()
        wzd = self.transfer_obj.browse([wzd_view['res_id']])
        wzd_line = wzd.item_ids[0]
        wzd_line.put_in_pack()
        packing = wzd_line.result_package_id
        wzd.do_detailed_transfer()
        self.assertEqual(self.picking1.state, 'done')
        self.picking2.signal_workflow('action_confirm')
        self.picking2.action_assign()
        self.picking2.force_assign()
        wzd_view2 = self.picking2.do_enter_transfer_details()
        wzd2 = self.transfer_obj.browse([wzd_view2['res_id']])
        val = {
            'transfer_id': wzd.id,
            'package_id': packing.id,
            'sourceloc_id': self.location_stock.id,
            'destinationloc_id': self.location_shelf2.id,
        }
        self.transfer_detail_obj.create(val)
        wzd2.do_detailed_transfer()
        self.assertEqual(self.picking2.state, 'done')
        self.assertEqual(packing.location_id.id, self.location_shelf2.id)
        self.assertEqual(self.picking2.created_inspections, 1)
