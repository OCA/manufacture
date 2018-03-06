# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo import fields
from odoo.exceptions import UserError


class TestMrpProductionRequest(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestMrpProductionRequest, self).setUp(*args, **kwargs)
        self.production_model = self.env['mrp.production']
        self.request_model = self.env['mrp.production.request']
        self.wiz_model = self.env['mrp.production.request.create.mo']
        self.bom_model = self.env['mrp.bom']

        self.product = self.env.ref('product.product_product_3')
        self.product.mrp_production_request = True

        self.test_product = self.env['product.product'].create({
            'name': 'Test Product without BoM',
            'mrp_production_request': True,
        })

        self.test_user = self.env['res.users'].create({
            'name': 'John',
            'login': 'test',
        })

    def create_procurement(self, name, product):
        values = {
            'name': name,
            'date_planned': fields.Datetime.now(),
            'product_id': product.id,
            'product_qty': 4.0,
            'product_uom': product.uom_id.id,
            'warehouse_id': self.env.ref('stock.warehouse0').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'route_ids': [
                (4, self.env.ref('mrp.route_warehouse0_manufacture').id, 0)],
        }
        return self.env['procurement.order'].create(values)

    def test_manufacture_request(self):
        """Tests manufacture request workflow."""
        proc = self.create_procurement('TEST/01', self.product)
        request = proc.mrp_production_request_id
        request.button_to_approve()
        request.button_draft()
        request.button_to_approve()
        request.button_approved()
        self.assertEqual(request.pending_qty, 4.0)
        wiz = self.wiz_model.with_context(active_ids=request.ids).create({})
        wiz.compute_product_line_ids()
        wiz.mo_qty = 4.0
        wiz.create_mo()
        mo = self.production_model.search([
            ('mrp_production_request_id', '=', request.id)])
        self.assertTrue(mo, "No MO created.")
        self.assertEqual(request.pending_qty, 0.0)
        request.button_done()

    def test_cancellation_from_request(self):
        """Tests propagation of cancel to procurements from manufacturing
        request and not from manufacturing order."""
        proc = self.create_procurement('TEST/02', self.product)
        request = proc.mrp_production_request_id
        wiz = self.wiz_model.with_context(active_ids=request.ids).create({})
        wiz.mo_qty = 4.0
        wiz.create_mo()
        with self.assertRaises(UserError):
            request.button_draft()
        mo = self.production_model.search([
            ('mrp_production_request_id', '=', request.id)])
        mo.action_cancel()
        self.assertNotEqual(proc.state, 'cancel')
        request.button_cancel()
        self.assertEqual(proc.state, 'cancel')

    def test_cancellation_from_proc(self):
        """Tests cancelation from procurement."""
        proc = self.create_procurement('TEST/03', self.product)
        request = proc.mrp_production_request_id
        self.assertNotEqual(request.state, 'cancel')
        proc.cancel()
        self.assertEqual(request.state, 'cancel')

    def test_assignation(self):
        """Tests assignation of manufacturing requests."""
        randon_bom_id = self.bom_model.search([], limit=1).id
        request = self.request_model.create({
            'assigned_to': self.test_user.id,
            'product_id': self.product.id,
            'product_qty': 5.0,
            'bom_id': randon_bom_id,
        })
        request._onchange_product_id()
        self.assertEqual(
            request.bom_id.product_tmpl_id, self.product.product_tmpl_id,
            "Wrong Bill of Materials.")
        request.write({
            'assigned_to': self.uid,
        })
        self.assertTrue(request.message_follower_ids,
                        "Followers not added correctly.")

    def test_raise_errors(self):
        """Tests user errors raising properly."""
        proc_no_bom = self.create_procurement('TEST/05', self.test_product)
        self.assertEqual(proc_no_bom.state, 'exception')
        proc = self.create_procurement('TEST/05', self.product)
        request = proc.mrp_production_request_id
        request.button_to_approve()
        proc.write({'state': 'done'})
        with self.assertRaises(UserError):
            request.button_cancel()
        with self.assertRaises(UserError):
            request.button_draft()
