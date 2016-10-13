# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


class TestMrpRepairDiscount(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestMrpRepairDiscount, cls).setUpClass()
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
            'standard_price': 10,
            'list_price': 20,
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
        })
        cls.location = cls.env['stock.location'].create({
            'name': 'Test location',
        })
        cls.repair = cls.env['mrp.repair'].create({
            'product_id': cls.product.id,
            'partner_id': cls.partner.id,
            'partner_invoice_id': cls.partner.id,
            'product_uom': cls.product.uom_id.id,
            'location_id': cls.location.id,
            'location_dest_id': cls.location.id,
            'invoice_method': 'b4repair',
        })
        cls.repair_line = cls.env['mrp.repair.line'].create({
            'repair_id': cls.repair.id,
            'type': 'add',
            'product_id': cls.product.id,
            'product_uom': cls.product.uom_id.id,
            'name': 'Test line',
            'location_id': cls.repair.location_id.id,
            'location_dest_id': cls.repair.location_dest_id.id,
            'product_uom_qty': 1,
            'price_unit': 20,
            'discount': 50,
            'to_invoice': True,
        })

    def test_discount(self):
        self.assertAlmostEqual(
            self.repair_line.price_subtotal, 10,
            self.repair_line._columns['price_subtotal'].digits[1])
        self.assertAlmostEqual(
            self.repair.amount_total, 10,
            self.repair._columns['amount_total'].digits[1])

    def test_invoice_create(self):
        self.repair.state = '2binvoiced'
        res = self.repair.action_invoice_create()
        invoice = self.env['account.invoice'].browse(res.values()[0])
        invoice_line = invoice.invoice_line[0]
        self.assertEqual(invoice_line.discount, 50)
        self.assertAlmostEqual(
            invoice_line.price_subtotal, 10,
            invoice_line._columns['price_subtotal'].digits[1])
