# -*- coding: utf-8 -*-
# © 2015 Avanzosc
# © 2015 Pedro M. Baeza - Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp.exceptions import Warning as UserError


class TestMrpHook(common.TransactionCase):
    def setUp(self):
        super(TestMrpHook, self).setUp()
        self.product_model = self.env['product.product']
        self.product = self.product_model.create({'name': 'Test product'})
        self.raw_product = self.product_model.create({'name': 'Raw product'})
        self.bom = self.env['mrp.bom'].create(
            {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_tmpl_id': self.product.product_tmpl_id.id,
                'bom_line_ids': [
                    (0, 0, {'product_id': self.raw_product.id,
                            'type': 'normal',
                            'product_qty': 2})]
            })

    def test_bom_explode_normal(self):
        products = self.bom._bom_explode(self.product, 1)[0]
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['product_id'], self.raw_product.id)
        self.assertEqual(products[0]['product_qty'], 2)

    def test_bom_explode_phantom_error(self):
        self.bom.bom_line_ids[0].type = 'phantom'
        with self.assertRaises(UserError):
            self.bom._bom_explode(self.product, 1)

    def test_bom_explode_phantom(self):
        self.bom.bom_line_ids[0].type = 'phantom'
        raw_product_2 = self.product_model.create({'name': 'Raw product 2'})
        self.env['mrp.bom'].create(
            {
                'name': self.raw_product.name,
                'product_id': self.raw_product.id,
                'product_tmpl_id': self.raw_product.product_tmpl_id.id,
                'bom_line_ids': [
                    (0, 0, {'product_id': raw_product_2.id,
                            'type': 'normal',
                            'product_qty': 3})]
            })
        products = self.bom._bom_explode(self.product, 1)[0]
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['product_id'], raw_product_2.id)
        self.assertEqual(products[0]['product_qty'], 6)
