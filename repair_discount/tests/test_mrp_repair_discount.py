# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestMrpRepairDiscount(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestMrpRepairDiscount, cls).setUpClass()
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
            'standard_price': 10,
            'list_price': 20,
        })
        cls.product_service = cls.env['product.product'].create({
            'name': 'Test product service',
            'standard_price': 10,
            'list_price': 20,
        })
        # cls.partner = cls.env['res.partner'].create({
        #     'name': 'Test partner',
        # })
        cls.partner = cls.env.ref('base.res_partner_address_1')
        cls.location = cls.env['stock.location'].create({
            'name': 'Test location',
        })
        cls.repair = cls.env['repair.order'].create({
            'product_id': cls.product.id,
            'partner_id': cls.partner.id,
            'partner_invoice_id': cls.partner.id,
            'product_uom': cls.product.uom_id.id,
            'location_id': cls.location.id,
            'invoice_method': 'b4repair',
        })
        domain_location = [('usage', '=', 'production')]
        stock_location_id = cls.env['stock.location'].search(domain_location, limit=1)
        cls.repair_line = cls.env['repair.line'].create({
            'repair_id': cls.repair.id,
            'type': 'add',
            'product_id': cls.product.id,
            'product_uom': cls.product.uom_id.id,
            'name': 'Test line',
            'location_id': cls.repair.location_id.id,
            'location_dest_id': stock_location_id.id,
            'product_uom_qty': 1,
            'price_unit': 20,
            'discount': 50,
        })

        cls.repair_fee = cls.env['repair.fee'].create({
            'repair_id': cls.repair.id,
            'name': 'Test Service',
            'product_id': cls.product_service.id,
            'product_uom_qty': 1,
            'product_uom': cls.product_service.uom_id.id,
            'price_unit': 20,
            'discount': 50,
        })

    def test_discount(self):
        self.assertAlmostEqual(
            self.repair_line.price_subtotal, 10)
        self.assertAlmostEqual(
            self.repair_fee.price_subtotal, 10)
        self.assertAlmostEqual(
            self.repair.amount_total, 20)

    def test_invoice_create(self):
        self.repair.state = '2binvoiced'
        res = self.repair.action_invoice_create()
        invoice = self.env['account.invoice'].browse(res.values())[0]
        invoice_line = invoice.invoice_line_ids[0]
        self.assertEqual(invoice_line.discount, 50)
        self.assertAlmostEqual(
            invoice_line.price_subtotal, 10)
