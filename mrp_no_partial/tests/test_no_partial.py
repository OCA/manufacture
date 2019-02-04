# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.exceptions import ValidationError


class TestNoPartial(common.TransactionCase):

    def setUp(self):
        super(TestNoPartial, self).setUp()
        self.production_obj = self.env['mrp.production']
        self.bom_obj = self.env['mrp.bom']
        self.location = self.env.ref('stock.stock_location_stock')
        self.picking_type = self.env.ref('mrp.picking_type_manufacturing')

        self.picking_type.mrp_no_partial = True

        self.uom = self.env.ref('product.product_uom_unit')

        self.product = self.env['product.product'].create({
            'name': 'Product MRP',
            'type': 'product',
            'uom_id': self.uom.id,
        })
        self.product_raw_material = self.env['product.product'].create({
            'name': 'Raw Material',
            'type': 'product',
            'uom_id': self.uom.id,
        })

        product_qty = self.env['stock.change.product.qty'].create({
            'location_id': self.location.id,
            'product_id': self.product_raw_material.id,
            'new_quantity': 100.0,
        })
        product_qty.change_product_qty()

        self.product_raw_material2 = self.env['product.product'].create({
            'name': 'Raw Material 2',
            'type': 'product',
            'uom_id': self.uom.id,
        })

        product_qty = self.env['stock.change.product.qty'].create({
            'location_id': self.location.id,
            'product_id': self.product_raw_material2.id,
            'new_quantity': 100.0,
        })
        product_qty.change_product_qty()

        self.bom = self.env['mrp.bom'].create({
            'product_id': self.product.id,
            'product_tmpl_id': self.product.product_tmpl_id.id,
            'bom_line_ids': ([
                (0, 0, {
                    'product_id': self.product_raw_material.id,
                    'product_qty': 5,
                    'product_uom_id': self.uom.id
                }),
                (0, 0, {
                    'product_id': self.product_raw_material2.id,
                    'product_qty': 4,
                    'product_uom_id': self.uom.id
                }),
            ])
        })

        # Create Production Order
        vals = {
            'picking_type_id': self.picking_type.id,
            'product_id': self.product.id,
            'product_qty': 1,
            'product_uom_id': self.uom.id,
            'bom_id': self.bom.id

        }
        self.production = self.production_obj.create(vals)

    def test_no_partial(self):
        self.production.action_assign()
        self.assertEquals(
            'assigned',
            self.production.availability,
        )
        # Check with no quantity done
        with self.assertRaises(ValidationError):
            self.production.button_mark_done()

        # Check with partial quantities
        for raw_move in self.production.move_raw_ids:
            raw_move.quantity_done += 1

        # Complete quantities
        for raw_move in self.production.move_raw_ids:
            raw_move.quantity_done = raw_move.quantity_available

        self.production.button_mark_done()

    def test_partial(self):
        self.picking_type.mrp_no_partial = False
        self.production.action_assign()
        self.production.button_mark_done()
