# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import TransactionCase


class TestProduct(TransactionCase):

    def setUp(self):
        super(TestProduct, self).setUp()
        product_model = self.env['product.product']

        self.p1_v1 = product_model.create({'name': 'Unittest P1 - Variant 1'})

        self.p1_v2 = product_model.create({
            'product_tmpl_id': self.p1_v1.product_tmpl_id.id,
            'name': 'Unittest P1 - Variant 2'
        })

        self.p1_tmpl = self.p1_v1.product_tmpl_id

        self.other_product = product_model.create({
            'name': 'Unittest - Other product'
        })

        self.component = product_model.create({
            'name': 'Unittest - componenet'
        })

    def test_product_action_view_bom(self):
        # Covering test

        result = self.p1_v1.action_view_bom()
        self.assertEqual('mrp.bom', result['res_model'])
        self.assertIn(('dismantling', '=', False), result['domain'])

    def test_product_action_view_dismantling_bom(self):
        # Covering test
        result = self.p1_v1.action_view_dismantling_bom()
        self.assertEqual('mrp.bom', result['res_model'])
        self.assertEqual(
            [('dismantling', '=', True),
             ('dismantled_product_id', '=', self.p1_v1.id)],
            result['domain']
        )

    def test_template_action_view_dismantling_bom(self):
        # Covering test
        result = self.p1_tmpl.action_view_dismantling_bom()
        self.assertEqual('mrp.bom', result['res_model'])
        self.assertEqual(
            [('dismantling', '=', True),
             ('dismantled_product_tmpl_id', '=', self.p1_tmpl.id)],
            result['domain']
        )

    def test_bom_count(self):
        self.assertEqual(0, self.p1_tmpl.bom_count)
        self.assertEqual(0, self.p1_v1.bom_count)

        # Create a BoM for this template (no variant)
        bom_model = self.env['mrp.bom']
        bom_model.create({'product_tmpl_id': self.p1_tmpl.id})

        self.assertEqual(1, self.p1_tmpl.bom_count)
        self.assertEqual(1, self.p1_v1.bom_count)
        self.assertEqual(1, self.p1_v2.bom_count)

        self.assertEqual(0, self.other_product.bom_count)

        # Create a BoM for variant 1
        v1_bom = bom_model.create({
            'product_tmpl_id': self.p1_tmpl.id,
            'product_id': self.p1_v1.id,
            'bom_line_ids': [(0, False, {
                'product_id': self.component.id
            })]
        })

        self.assertEqual(2, self.p1_tmpl.bom_count)
        self.assertEqual(2, self.p1_v1.bom_count)
        self.assertEqual(1, self.p1_v2.bom_count)

        self.assertEqual(0, self.other_product.bom_count)

        # Create a dismantling BoM for other product
        # with P1 template as main component.
        bom_model.create({
            'product_tmpl_id': self.p1_tmpl.id,
            'dismantling': True,
            'dismantled_product_id': self.other_product.id
        })

        self.assertEqual(2, self.p1_tmpl.bom_count)
        self.assertEqual(0, self.p1_tmpl.dismantling_bom_count)

        self.assertEqual(2, self.p1_v1.bom_count)
        self.assertEqual(0, self.p1_v1.dismantling_bom_count)

        self.assertEqual(1, self.p1_v2.bom_count)
        self.assertEqual(0, self.p1_v2.dismantling_bom_count)

        self.assertEqual(0, self.other_product.bom_count)
        self.assertEqual(1, self.other_product.dismantling_bom_count)

        # Create a dismantling BoM for P1 V1
        v1_bom.create_dismantling_bom()

        self.assertEqual(2, self.p1_tmpl.bom_count)
        self.assertEqual(1, self.p1_tmpl.dismantling_bom_count)

        self.assertEqual(2, self.p1_v1.bom_count)
        self.assertEqual(1, self.p1_v1.dismantling_bom_count)

        self.assertEqual(1, self.p1_v2.bom_count)
        self.assertEqual(0, self.p1_v2.dismantling_bom_count)

        self.assertEqual(0, self.other_product.bom_count)
        self.assertEqual(1, self.other_product.dismantling_bom_count)
