# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import TransactionCase


class TestTemplate(TransactionCase):

    def test_bom_count(self):
        tmpl_model = self.env['product.template']

        tmpl1 = tmpl_model.create({'name': 'Template 1'})
        self.assertEqual(0, tmpl1.bom_count)

        # Create a BoM for this template
        bom_model = self.env['mrp.bom']
        bom_model.create({'product_tmpl_id': tmpl1.id})

        self.assertEqual(1, tmpl1.bom_count)

        # Create a dismantling BoM
        other_product = self.env['product.product'].create({
            'name': 'Other product'
        })

        bom_model.create({
            'product_tmpl_id': tmpl1.id,
            'dismantling': True,
            'dismantled_product_id': other_product.id
        })

        self.assertEqual(1, tmpl1.bom_count)

        # Check count on another template
        tmpl2 = tmpl_model.create({'name': 'Template 2'})
        self.assertEqual(0, tmpl2

                         .bom_count)

        # And on dismantled product
        self.assertEqual(0, other_product.product_tmpl_id.bom_count)
