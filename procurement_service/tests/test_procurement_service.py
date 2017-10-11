# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import odoo.tests.common as common


class TestProcurementService(common.TransactionCase):
    def setUp(self):
        super(TestProcurementService, self).setUp()
        self.product_model = self.env['product.product']
        self.partner_model = self.env['res.partner']
        self.purchase_order_model = self.env['purchase.order']
        self.sale_model = self.env['sale.order']
        self.sale_line_model = self.env['sale.order.line']
        self.procurement_model = self.env['procurement.order']

        service_product_vals = {
            'name': 'Service Generated Procurement',
            'standard_price': 20.5,
            'list_price': 30.75,
            'type': 'service',
            'route_ids': [(6, 0,
                           [self.env.ref('stock.route_warehouse0_mto').id,
                            self.env.ref('purchase.route_warehouse0_buy').id
                            ])]}
        consumable_product_vals = {
            'name': 'Consumable Generated Procurement',
            'standard_price': 20.5,
            'list_price': 30.75,
            'type': 'consu',
            'route_ids': [(6, 0,
                           [self.env.ref('stock.route_warehouse0_mto').id,
                            self.env.ref('purchase.route_warehouse0_buy').id
                            ])]}
        seller_vals = {'name': self.env.ref('base.res_partner_2').id}
        service_product_vals['seller_ids'] = [(0, 0, seller_vals)]
        consumable_product_vals['seller_ids'] = [(0, 0, seller_vals)]
        self.service_product = \
            self.product_model.create(service_product_vals)
        self.consumable_product = \
            self.product_model.create(consumable_product_vals)

        partner_vals = {'name': 'Customer for procurement service',
                        'customer': True}
        self.partner = self.partner_model.create(partner_vals)
        service_sale_vals = {
            'partner_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'pricelist_id': self.env.ref('product.list0').id,
            'picking_policy': 'direct'}
        service_sale_line_vals = {
            'product_id': self.service_product.id,
            'name': self.service_product.name,
            'product_uom_qty': 1,
            'product_uom': self.service_product.uom_id.id,
            'price_unit': self.service_product.list_price}
        consumable_sale_line_vals = {
            'product_id': self.consumable_product.id,
            'name': self.service_product.name,
            'product_uom_qty': 1,
            'product_uom': self.service_product.uom_id.id,
            'price_unit': self.service_product.list_price}
        service_sale_vals['order_line'] = [(0, 0, service_sale_line_vals)]
        self.service_sale_order = \
            self.sale_model.create(service_sale_vals.copy())
        mixed_sale_vals = service_sale_vals
        mixed_sale_vals['order_line'] = [
            (0, 0, service_sale_line_vals),
            (0, 0, consumable_sale_line_vals)]
        self.mixed_sale_order = \
            self.sale_model.create(mixed_sale_vals.copy())

    def test_confirm_service_sale(self):
        """Confirming the sale order generates the service procurement"""
        self.service_sale_order.action_confirm()
        for line in self.service_sale_order.order_line:
            cond = [('sale_line_id', '=', line.id)]
            procs = self.procurement_model.search(cond)
            self.assertEqual(
                len(procs), 1,
                "Procurement not generated for the service product type")
            procs[0]._run()
            procs[0]._check()
            self.assertNotEqual(
                procs[0].purchase_line_id, False,
                "Procurement without purchase line")
            procs[0].purchase_line_id.order_id.state = 'done'
            procs[0]._check()

    def test_confirm_mixed_sale(self):
        """Confirming a mixed sale order generates
        only one purchase order"""
        self.mixed_sale_order.action_confirm()
        pos_nbr = self.purchase_order_model.search_count([
            ('origin', 'like', self.mixed_sale_order.name)])
        self.assertEquals(pos_nbr, 1,
                          "Multiple purchase orders have been created")
