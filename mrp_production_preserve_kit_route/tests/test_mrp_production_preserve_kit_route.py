# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestMrpProductionPreserveKitRoute(TestMrpCommon):

    def setUp(self):
        super(TestMrpProductionPreserveKitRoute, self).setUp()
        vendor = self.env['res.partner'].create({
            'name': 'Partner #2',
        })
        supplierinfo = self.env['product.supplierinfo'].create({
            'name': vendor.id,
        })
        # Acoustic Bloc Screens, 16 on hand
        self.product1 = self.env.ref('product.product_product_25')
        # Large Cabinet, 250 on hand
        self.product3 = self.env.ref('product.product_product_6')
        # Drawer Black, 0 on hand
        self.product4 = self.env.ref('product.product_product_16')
        self.product2 = self.env['product.product'].create({
            'name': 'Component product',
            'default_code': 'code1234',
            'type': 'product',
            'purchase_ok': True,
            'route_ids': [
                (4, self.env.ref('purchase_stock.route_warehouse0_buy').id),
                (4, self.env.ref('stock.route_warehouse0_mto').id)],
            'seller_ids': [(6, 0, [supplierinfo.id])],
        })
        self.product_bom = self.env['product.product'].create({
            'name': 'Product with bom',
            'route_ids': [(4, self.env.ref('mrp.route_warehouse0_manufacture').id),
                          (4, self.env.ref('stock.route_warehouse0_mto').id)],
            'default_code': 'code123',
            'type': 'product',
            'sale_ok': True,
        })
        self.product_kit = self.env['product.product'].create({
            'name': 'Product with kit bom',
            'route_ids': [(4, self.env.ref('mrp.route_warehouse0_manufacture').id),
                          (4, self.env.ref('stock.route_warehouse0_mto').id)],
            'default_code': 'code1234',
            'type': 'product',
            'sale_ok': True,
        })
        kit_component_values = [{
            'product_id': x.id,
            'product_qty': 1,
        } for x in self.product1 | self.product2]
        self.kit = self.env['mrp.bom'].create({
            'product_tmpl_id': self.product_kit.product_tmpl_id.id,
            'code': self.product_kit.default_code,
            'type': 'phantom',
            'product_qty': 1,
            'product_uom_id': self.env.ref('uom.product_uom_unit').id,
            'bom_line_ids': [
                (0, 0, x) for x in kit_component_values]
        })
        bom_component_values = [{
            'product_id': x.id,
            'product_qty': 1,
        } for x in self.product3 | self.product4 | self.product_kit]
        self.bom = self.env['mrp.bom'].create({
            'product_tmpl_id': self.product_bom.product_tmpl_id.id,
            'code': self.product_bom.default_code,
            'type': 'normal',
            'product_qty': 1,
            'product_uom_id': self.env.ref('uom.product_uom_unit').id,
            'bom_line_ids': [
                (0, 0, x) for x in bom_component_values]
        })

    def test_so_bom_kit(self):
        man_order = self.env['mrp.production'].create({
            'name': 'MO-Test',
            'product_id': self.product_bom.id,
            'product_uom_id': self.product_bom.uom_id.id,
            'product_qty': 1,
            'bom_id': self.bom.id,
        })
        self.assertEqual(len(man_order.move_raw_ids), 4)
        self.assertEqual(set(man_order.move_raw_ids.filtered(
            lambda x: x.product_id != self.product2
        ).mapped('procure_method')), {'make_to_stock'})
        self.assertEqual(set(man_order.move_raw_ids.filtered(
            lambda x: x.product_id == self.product2
        ).mapped('procure_method')), {'make_to_order'})
