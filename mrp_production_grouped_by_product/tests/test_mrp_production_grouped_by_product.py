# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestProductionGroupedByProduct(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestProductionGroupedByProduct, cls).setUpClass()
        cls.product1 = cls.env['product.product'].create({
            'name': 'TEST Muffin',
            'route_ids': [(6, 0, [
                cls.env.ref('mrp.route_warehouse0_manufacture').id])],
            'type': 'product',
        })
        cls.product2 = cls.env['product.product'].create({
            'name': 'TEST Paper muffin cup',
            'type': 'product',
        })
        cls.product3 = cls.env['product.product'].create({
            'name': 'TEST Muffin paset',
            'type': 'product',
        })
        cls.bom = cls.env['mrp.bom'].create({
            'product_id': cls.product1.id,
            'product_tmpl_id': cls.product1.product_tmpl_id.id,
            'type': 'normal',
            'bom_line_ids': [(0, 0, {
                'product_id': cls.product2.id,
                'product_qty': 1,
            }), (0, 0, {
                'product_id': cls.product3.id,
                'product_qty': 0.2,
            })]
        })
        cls.env['stock.change.product.qty'].create({
            'product_id': cls.product2.id,
            'new_quantity': 100.0,
        }).change_product_qty()
        cls.env['stock.change.product.qty'].create({
            'product_id': cls.product3.id,
            'new_quantity': 100.0,
        }).change_product_qty()
        cls.stock_picking_type = cls.env.ref('stock.picking_type_out')
        cls.procurement_rule = cls.env['stock.warehouse.orderpoint'].create({
            'name': 'XXX/00000',
            'product_id': cls.product1.id,
            'product_min_qty': 10,
            'product_max_qty': 100,
        })

    def test_mo_by_product(self):
        self.env['procurement.group'].run_scheduler()
        mo = self.env['mrp.production'].search([
            ('product_id', '=', self.product1.id),
        ])
        self.assertTrue(mo)
        #
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.stock_picking_type.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref(
                'stock.stock_location_customers').id,
        })
        move = self.env['stock.move'].create({
            'name': self.product1.name,
            'product_id': self.product1.id,
            'product_uom_qty': 1000,
            'product_uom': self.product1.uom_id.id,
            'picking_id': picking.id,
            'picking_type_id': self.stock_picking_type.id,
            'location_id': picking.location_id.id,
            'location_dest_id': picking.location_id.id,
        })
        move.quantity_done = 1000
        picking.action_assign()
        self.product1.virtual_available = -500
        self.env['procurement.group'].run_scheduler()
        mo = self.env['mrp.production'].search([
            ('product_id', '=', self.product1.id),
        ])
        self.assertEqual(len(mo), 1)
