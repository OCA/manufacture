# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp import fields


class TestMrpMtoWithStock(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestMrpMtoWithStock, self).setUp(*args, **kwargs)
        self.production_model = self.env['mrp.production']
        self.bom_model = self.env['mrp.bom']
        self.stock_location_stock = self.env.ref('stock.stock_location_stock')
        self.manufacture_route = self.env.ref(
            'mrp.route_warehouse0_manufacture')
        self.uom_unit = self.env.ref('product.product_uom_unit')

        self.product_fp = self.env['product.product'].create({
            'name': 'FP',
            'type': 'product',
            'uom_id': self.uom_unit.id,
            'route_ids': [(4, self.manufacture_route.id)]
        })
        self.product_c1 = self.env['product.product'].create({
            'name': 'C1',
            'type': 'product',
            'uom_id': self.uom_unit.id,
            'route_ids': [(4, self.manufacture_route.id)]
        })
        self.product_c2 = self.env['product.product'].create({
            'name': 'C2',
            'type': 'product',
            'uom_id': self.uom_unit.id,
        })
        self._update_product_qty(self.product_c2,
                                 self.stock_location_stock, 10)

        self.bom_fp = self.env['mrp.bom'].create({
            'product_id': self.product_fp.id,
            'product_tmpl_id': self.product_fp.product_tmpl_id.id,
            'bom_line_ids': ([
                (0, 0, {
                    'product_id': self.product_c1.id,
                    'product_qty': 1,
                    'product_uom': self.uom_unit.id
                }),
                (0, 0, {
                    'product_id': self.product_c2.id,
                    'product_qty': 1,
                    'product_uom': self.uom_unit.id
                }),
            ])
        })

        self.bom_c1 = self.env['mrp.bom'].create({
            'product_id': self.product_c1.id,
            'product_tmpl_id': self.product_c1.product_tmpl_id.id,
            'bom_line_ids': ([(0, 0, {
                'product_id': self.product_c2.id,
                'product_qty': 1,
                'product_uom': self.uom_unit.id
            })])
        })
        self.product_c1.mrp_mts_mto_location_ids = [
            (6, 0, [self.stock_location_stock.id])]

    def _update_product_qty(self, product, location, quantity):
        """Update Product quantity."""
        product_qty = self.env['stock.change.product.qty'].create({
            'location_id': location.id,
            'product_id': product.id,
            'new_quantity': quantity,
        })
        product_qty.change_product_qty()
        return product_qty

    def create_procurement(self, name, product):
        values = {
            'name': name,
            'date_planned': fields.Datetime.now(),
            'product_id': product.id,
            'product_qty': 4.0,
            'product_uom': product.uom_id.id,
            'warehouse_id': self.env.ref('stock.warehouse0').id,
            'location_id': self.stock_location_stock.id,
            'route_ids': [
                (4, self.env.ref('mrp.route_warehouse0_manufacture').id, 0)],
        }
        return self.env['procurement.order'].create(values)

    def test_manufacture(self):

        procurement_fp = self.create_procurement('TEST/01', self.product_fp)
        production_fp = procurement_fp.production_id
        self.assertEqual(production_fp.state, 'confirmed')

        production_fp.action_assign()
        self.assertEqual(production_fp.state, 'confirmed')

        procurement_c1 = self.env['procurement.order'].search(
            [('product_id', '=', self.product_c1.id),
             ('move_dest_id', 'in', production_fp.move_lines.ids)], limit=1)
        self.assertEquals(len(procurement_c1), 1)

        procurement_c2 = self.env['procurement.order'].search(
            [('product_id', '=', self.product_c2.id),
             ('move_dest_id', 'in', production_fp.move_lines.ids)], limit=1)
        self.assertEquals(len(procurement_c2), 0)

        procurement_c1.run()
        production_c1 = procurement_c1.production_id
        self.assertEqual(production_c1.state, 'confirmed')

        production_c1.action_assign()
        self.assertEqual(production_c1.state, 'ready')

        procurement_c2 = self.env['procurement.order'].search(
            [('product_id', '=', self.product_c2.id),
             ('move_dest_id', 'in', production_c1.move_lines.ids)], limit=1)
        self.assertEquals(len(procurement_c2), 0)

        wizard = self.env['mrp.product.produce'].create({
            'product_id': self.product_c1.id,
            'product_qty': 1,
        })
        self.env['mrp.production'].action_produce(
            production_c1.id, 1, 'consume_produce', wizard)
        production_c1.refresh()
        self.assertEqual(production_fp.state, 'confirmed')

        wizard = self.env['mrp.product.produce'].create({
            'product_id': self.product_c1.id,
            'product_qty': 3,
        })
        self.env['mrp.production'].action_produce(
            production_c1.id, 3, 'consume_produce', wizard)
        production_c1.refresh()
        self.assertEqual(production_fp.state, 'ready')
