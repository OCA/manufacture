# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestMrpProductionUnreserve(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestMrpProductionUnreserve, self).setUp(*args, **kwargs)
        self.production_model = self.env['mrp.production']
        self.bom_model = self.env['mrp.bom']
        self.product_model = self.env['product.product']
        self.quant_model = self.env['stock.quant']

        # Create products, BoM and MO:
        self.product = self.product_model.create({
            'name': 'Test Product',
            'type': 'product',
        })
        self.component_a = self.product_model.create({
            'name': 'Component A',
            'type': 'product',
        })
        self.component_b = self.product_model.create({
            'name': 'Component B',
            'type': 'product',
        })
        self.test_bom = self.bom_model.create({
            'product_tmpl_id': self.product.product_tmpl_id.id,
            'product_qty': 1,
            'code': 'TEST',
            'bom_line_ids': [
                (0, 0, {
                    'product_id': self.component_a.id,
                    'product_qty': 2,
                }),
                (0, 0, {
                    'product_id': self.component_b.id,
                    'product_qty': 1,
                })
            ],
        })
        self.test_mo = self.production_model.create({
            'product_id': self.product.id,
            'product_qty': 5.0,
            'product_uom': self.product.uom_id.id,
            'bom_id': self.test_bom.id,
        })
        # Create Stock for components:
        wh_main = self.browse_ref('stock.warehouse0')
        stock_location_id = wh_main.lot_stock_id.id
        self.quant_model.create({
            'product_id': self.component_a.id,
            'location_id': stock_location_id,
            'qty': 10.0,
        })
        self.quant_model.create({
            'product_id': self.component_b.id,
            'location_id': stock_location_id,
            'qty': 5.0,
        })

    def test_mo_unreserve(self):
        self.test_mo._compute_unreserve_visible()
        self.assertFalse(self.test_mo.unreserve_visible)
        self.assertFalse(self.test_mo.move_lines)
        self.test_mo.action_confirm()
        self.test_mo.action_assign()
        for l in self.test_mo.move_lines:
            self.assertEqual(l.state, 'assigned')
        self.test_mo._compute_unreserve_visible()
        self.assertTrue(self.test_mo.unreserve_visible)
        self.test_mo.button_unreserve()
        for l in self.test_mo.move_lines:
            self.assertEqual(l.state, 'confirmed')
