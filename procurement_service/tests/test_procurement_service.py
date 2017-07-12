# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestProcurementService(common.TransactionCase):

    def setUp(self):
        super(TestProcurementService, self).setUp()
        self.product_model = self.env['product.product']
        self.partner_model = self.env['res.partner']
        self.sale_model = self.env['sale.order']
        self.sale_line_model = self.env['sale.order.line']
        self.procurement_model = self.env['procurement.order']
        product_vals = {
            'name': 'Service Generated Procurement',
            'standard_price': 20.5,
            'list_price': 30.75,
            'type': 'service',
            'route_ids': [(6, 0,
                           [self.env.ref('stock.route_warehouse0_mto').id,
                            self.env.ref('purchase.route_warehouse0_buy').id
                            ])]}
        seller_vals = {'name': self.env.ref('base.res_partner_2').id}
        product_vals['seller_ids'] = [(0, 0, seller_vals)]
        self.service_product = self.product_model.create(product_vals)
        partner_vals = {'name': 'Customer for procurement service',
                        'customer': True}
        self.partner = self.partner_model.create(partner_vals)
        sale_vals = {'partner_id': self.partner.id,
                     'partner_shipping_id': self.partner.id,
                     'partner_invoice_id': self.partner.id,
                     'pricelist_id': self.env.ref('product.list0').id,
                     'picking_policy': 'direct'}
        sale_line_vals = {'product_id': self.service_product.id,
                          'name': self.service_product.name,
                          'product_uos_qty': 1,
                          'product_uom': self.service_product.uom_id.id,
                          'price_unit': self.service_product.list_price}
        sale_vals['order_line'] = [(0, 0, sale_line_vals)]
        self.sale_order = self.sale_model.create(sale_vals)

    def test_confirm_sale_and_generate_procurement_service(self):
        self.sale_order.action_button_confirm()
        for line in self.sale_order.order_line:
            cond = [('sale_line_id', '=', line.id)]
            procs = self.procurement_model.search(cond)
            self.assertEqual(
                len(procs), 1,
                "Procurement not generated for the service product type")
            self.procurement_model._run(procs[0])
            self.procurement_model._check(procs[0])
            self.assertNotEqual(
                procs[0].purchase_line_id, False,
                "Procurement without purchase line")
            procs[0].purchase_line_id.order_id.state = 'done'
            self.procurement_model._check(procs[0])
