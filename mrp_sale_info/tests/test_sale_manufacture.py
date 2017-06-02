# -*- coding: utf-8 -*-
# © 2017 Bima Jati Wijaya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestManufactureSale(TransactionCase):

    def setUp(self):
        super(TestManufactureSale, self).setUp()
        self.partner = self.env.ref('base.res_partner_1')
        self.mrp_production = self.env['mrp.production']

    def test_manufacture(self):
        product = self.browse_ref('product.product_product_27')
        route1 = self.browse_ref('mrp.route_warehouse0_manufacture')
        route2 = self.browse_ref('stock.route_warehouse0_mto')
        # add make to order and manufacture routes
        product.write({'route_ids': [(6, 0, [route1.id, route2.id])]})
        self.assertTrue(product.route_ids)

        so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [(0, 0, {'name': product.name,
                                   'product_id': product.id,
                                   'product_uom_qty': 1,
                                   'product_uom': product.uom_id.id,
                                   'price_unit': product.list_price})
                           ],
            'pricelist_id': self.env.ref('product.list0').id,
        })
        so.action_confirm()
        mrp = self.mrp_production.search([('origin', 'like', so.name+'%')],
                                         limit=1)
        # checking sale info filled correctly on manufacture
        self.assertEqual(so.id, mrp.sale_id.id)
        self.assertEqual(self.partner.id, mrp.partner_id.id)
        self.assertEqual(so.commitment_date, mrp.commitment_date)
