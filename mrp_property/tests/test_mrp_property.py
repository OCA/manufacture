# coding: utf-8
# Copyright 2018 Opener B.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase
from odoo.exceptions import UserError


class TestBomProperty(SavepointCase):
    def setUp(self):
        super(TestBomProperty, self).setUp()
        self.product = self.env.ref('product.product_product_3')
        self.group = self.env['mrp.property.group'].create({'name': __name__})
        self.property1 = self.env['mrp.property'].create({
            'name': 'prop1',
            'group_id': self.group.id,
        })
        self.property2 = self.env['mrp.property'].create({
            'name': 'prop2',
            'group_id': self.group.id,
        })
        self.bom_without_properties = self.env.ref('mrp.mrp_bom_manufacture')
        self.bom_with_properties = self.env.ref(
            'mrp.mrp_bom_manufacture').copy({
                'sequence': '999',
                'property_ids':
                [(6, 0, [self.property1.id, self.property2.id])]})
        partner = self.env.ref('base.res_partner_address_7')
        self.order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'pricelist_id': self.env.ref('product.list0').id,
        })
        self.line = self.env['sale.order.line'].create({
            'order_id': self.order.id,
            'product_id':  self.product.id,
            'product_uom_qty': 2,
        })
        self.last_production_id = (
            self.env['mrp.production'].search(
                [('product_id', '=', self.product.id)],
                order='id desc', limit=1).id or 0)

    def test_01_no_properties(self):
        """ BoM with the lowest sequence is selected for a line w/o properties
        """
        self.order.action_confirm()
        production = self.env['mrp.production'].search(
            [('product_id', '=', self.product.id),
             ('id', '>', self.last_production_id)])
        self.assertTrue(production)
        self.assertEqual(production.bom_id, self.bom_without_properties)

    def test_02_one_property(self):
        """ Without a BoM with all the properties, the fallback is selected """
        self.line.property_ids = self.property1
        self.order.action_confirm()
        production = self.env['mrp.production'].search(
            [('product_id', '=', self.product.id),
             ('id', '>', self.last_production_id)])
        self.assertTrue(production)
        self.assertEqual(
            production.bom_id, self.bom_without_properties)

    def test_03_two_properties(self):
        """ The BoM with all the properties is selected """
        self.line.property_ids = self.property1 + self.property2
        self.order.action_confirm()
        production = self.env['mrp.production'].search(
            [('product_id', '=', self.product.id),
             ('id', '>', self.last_production_id)])
        self.assertTrue(production)
        self.assertEqual(
            production.bom_id, self.bom_with_properties)

    def test_04_one_property_no_fallback(self):
        """ Without a fallback BoM, the procurement cannot proceed """
        self.line.property_ids = self.property1
        self.bom_without_properties.active = False
        self.order.action_confirm()
        production = self.env['mrp.production'].search(
            [('product_id', '=', self.product.id),
             ('id', '>', self.last_production_id)])
        self.assertFalse(production)

    def test_05_delete_properties(self):
        """ Cannot delete properties that are in use """
        self.line.property_ids = self.property1 + self.property2
        with self.assertRaises(UserError):
            self.property2.unlink()
        self.line.property_ids = self.property1
        self.property2.unlink()
