# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMrpMtoWithStock(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestMrpMtoWithStock, self).setUp(*args, **kwargs)
        self.repair_obj = self.env['mrp.repair']
        self.repair_line_obj = self.env['mrp.repair.line']
        self.product_obj = self.env['product.product']
        self.move_obj = self.env['stock.move']

        self.stock_location_stock = self.env.ref('stock.stock_location_stock')
        self.customer_location = self.env.ref('stock.stock_location_customers')
        self.refurbish_loc = self.env.ref(
            'mrp_repair_refurbish.stock_location_refurbish')

        self.refurbish_product = self.product_obj.create({
            'name': 'Refurbished Awesome Screen',
            'type': 'product',
        })
        self.product = self.product_obj.create({
            'name': 'Awesome Screen',
            'type': 'product',
            'refurbish_product_id': self.refurbish_product.id,
        })
        self.material = self.product_obj.create({
            'name': 'Materials',
            'type': 'consu',
        })
        self._update_product_qty(self.product, self.stock_location_stock, 10.0)

    def _update_product_qty(self, product, location, quantity):
        product_qty = self.env['stock.change.product.qty'].create({
            'location_id': location.id,
            'product_id': product.id,
            'new_quantity': quantity,
        })
        product_qty.change_product_qty()
        return product_qty

    def test_01_repair_refurbish(self):
        """Tests that locations are properly set with a product to
        refurbish, then complete repair."""
        repair = self.repair_obj.create({
            'product_id': self.product.id,
            'product_qty': 3.0,
            'product_uom': self.product.uom_id.id,
            'location_dest_id': self.customer_location.id,
        })
        repair.onchange_product_id()
        self.assertTrue(repair.to_refurbish)
        repair._onchange_to_refurbish()
        self.assertEqual(repair.refurbish_location_dest_id,
                         self.customer_location)
        self.assertEqual(repair.location_dest_id,
                         self.product.property_stock_refurbish)
        line = self.repair_line_obj.with_context(
            to_refurbish=repair.to_refurbish,
            refurbish_location_dest_id=repair.refurbish_location_dest_id,
        ).new({
            'name': 'consume stuff to repair',
            'repair_id': repair.id,
            'type': 'add',
            'product_id': self.material.id,
            'product_uom': self.material.uom_id.id,
            'product_uom_qty': 1.0,
        })
        line.onchange_product_id()
        line.onchange_operation_type()
        self.assertEqual(line.location_id, repair.location_id)
        self.assertEqual(line.location_dest_id, self.customer_location)
        # Complete repair:
        repair.action_validate()
        repair.action_repair_start()
        repair.action_repair_end()
        moves = self.move_obj.search([('reference', '=', repair.name)])
        self.assertEqual(len(moves), 2)
        for m in moves:
            self.assertEqual(m.state, 'done')
            if m.product_id == self.product:
                self.assertEqual(m.location_id, self.stock_location_stock)
                self.assertEqual(m.location_dest_id, self.refurbish_loc)
            elif m.product_id == self.refurbish_product:
                self.assertEqual(m.location_id, self.refurbish_loc)
                self.assertEqual(m.location_dest_id, self.customer_location)
            else:
                self.assertTrue(False, "Unexpected move.")
