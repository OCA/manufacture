# -*- coding: utf-8 -*-
# Copyright 2017 Bima Wijaya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import common


class TestMrpProperty(common.TransactionCase):

    def setUp(self):
        super(TestMrpProperty, self).setUp()
        self.product_laptop = self.browse_ref('product.product_product_27')
        self.prop_group_id = self.env['mrp.property.group'].create(
            {'name': 'group test'})
        self.property_1 = self.env['mrp.property'].create({
            'name': 'property 1',
            'composition': 'min',
            'group_id': self.prop_group_id.id,
        })
        self.property_2 = self.env['mrp.property'].create({
            'name': 'property 2',
            'composition': 'plus',
            'group_id': self.prop_group_id.id,
        })
        self.manufacture = self.browse_ref('mrp.route_warehouse0_manufacture')
        self.mto = self.browse_ref('stock.route_warehouse0_mto')
        self.product_laptop.write({'route_ids': [(6, 0, [self.manufacture.id,
                                                         self.mto.id])]})

        self.bom1 = self.browse_ref('mrp.mrp_bom_laptop_cust')
        self.bom1.bom_line_ids[0].unlink()
        self.bom1.write({'property_ids': [(6, 0, [self.property_1.id])]})

        self.bom2 = self.browse_ref('mrp.mrp_bom_laptop_cust_rout')
        self.bom2.write({'property_ids': [(6, 0, [self.property_2.id])]})

        self.bom3 = self.bom2.copy()
        self.bom3.write({'property_ids': [(6, 0, [self.property_1.id,
                                                  self.property_2.id])],
                         'sequence': self.bom3.sequence - 1})
        self.partner = self.env.ref('base.res_partner_1')

    def test_sales_mrp(self):
        so_vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [(0, 0, {
                'name': self.product_laptop.name,
                'product_id': self.product_laptop.id,
                'product_uom_qty': 5.0,
                'product_uom': self.product_laptop.uom_id.id,
                'property_ids': [(6, 0, [self.property_2.id])],
                'price_unit': self.product_laptop.list_price})],
            'pricelist_id': self.env.ref('product.list0').id,
        }
        so = self.env['sale.order'].create(so_vals)
        so.action_confirm()

        mrp_test = self.env['mrp.production'].search([
            ('origin', 'ilike', '%' + so.name + '%')])
        self.assertEqual(mrp_test.property_ids, so.order_line.property_ids,
                         "Different property between MRP and SO")
        self.assertEqual(mrp_test.bom_id.property_ids,
                         so.order_line.property_ids,
                         "Different property between BOM MO and SO")
        self.assertEqual(mrp_test.bom_id, self.bom2, "Wrong select BoM!")

    def test_sales_mrp2(self):
        # Should return BoM which have all spesified properties
        so_vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [(0, 0, {
                'name': self.product_laptop.name,
                'product_id': self.product_laptop.id,
                'product_uom_qty': 5.0,
                'product_uom': self.product_laptop.uom_id.id,
                'property_ids': [(6, 0, [self.property_1.id,
                                         self.property_2.id])],
                'price_unit': self.product_laptop.list_price})],
            'pricelist_id': self.env.ref('product.list0').id,
        }
        so = self.env['sale.order'].create(so_vals)
        so.action_confirm()

        mrp_test = self.env['mrp.production'].search([
            ('origin', 'ilike', '%' + so.name + '%')])
        self.assertEqual(mrp_test.property_ids, so.order_line.property_ids,
                         "Different property between MRP and SO")
        self.assertEqual(mrp_test.bom_id.property_ids,
                         so.order_line.property_ids,
                         "Different property between BOM MO and SO")
        self.assertEqual(mrp_test.bom_id, self.bom3, "Wrong select BoM!")
