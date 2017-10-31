# -*- coding: utf-8 -*-
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProcurementOrder(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestProcurementOrder, self).setUp()
        self.product_model = self.env['product.product']
        self.partner_model = self.env['res.partner']
        self.sale_model = self.env['sale.order']
        self.project_task_model = self.env['project.task']

        service_product_vals = {
            'name': 'Service Generated Procurement',
            'standard_price': 20.5,
            'list_price': 30.75,
            'type': 'service',
            'route_ids': [(6, 0,
                           [self.env.ref('stock.route_warehouse0_mto').id,
                            self.env.ref('purchase.route_warehouse0_buy').id
                            ])]}
        seller_vals = {'name': self.env.ref('base.res_partner_2').id}
        service_product_vals['seller_ids'] = [(0, 0, seller_vals)]
        self.service_product = \
            self.product_model.create(service_product_vals)

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
        service_sale_vals['order_line'] = [(0, 0, service_sale_line_vals)]
        self.service_sale_order = \
            self.sale_model.create(service_sale_vals.copy())

    def test_create_project_and_task(self):
        self.service_sale_order.action_confirm()
        for line in self.service_sale_order.order_line:
            cond = [('sale_line_id', '=', line.id)]
            tasks = self.project_task_model.search(cond)
            self.assertGreater(len(tasks), 0, "Task not created")
