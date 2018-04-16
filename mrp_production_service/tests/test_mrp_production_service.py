# -*- coding: utf-8 -*-
# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestMrpProductionService(TransactionCase):
    def setUp(self):
        super(TestMrpProductionService, self).setUp()
        # Create products
        product_model = self.env['product.product']
        self.p1 = product_model.create({'name': '101'})
        self.p2 = product_model.create({'name': '201P'})
        self.p3 = product_model.create({'name': '202P'})
        self.service = product_model.create({'name': 'Assembly Service',
                                             'type': 'service'})

        # Create bill of materials
        self.bom_model = self.env['mrp.bom']
        self.bom = self.bom_model.create({
            'product_tmpl_id': self.p1.product_tmpl_id.id,
            'product_id': self.p1.id,
            'product_qty': 1,
            'type': 'normal',
        })
        # Create bom lines
        self.bom_line_model = self.env['mrp.bom.line']
        self.bom_line_model.create({
            'bom_id': self.bom.id,
            'product_id': self.p2.id,
            'product_qty': 1,
        })
        self.bom_line_model.create({
            'bom_id': self.bom.id,
            'product_id': self.p3.id,
            'product_qty': 1,
        })
        self.bom_line_model.create({
            'bom_id': self.bom.id,
            'product_id': self.service.id,
            'product_qty': 1,
        })

    def test_produce_bom_with_service(self):
        """Explode bill of material and look for a procurement of a service."""
        self.mrp_production_model = self.env['mrp.production']

        self.env['mrp.production'].create({
            'product_id': self.p1.id,
            'product_qty': 1.0,
            'product_uom_id': self.p1.uom_id.id,
            'bom_id': self.bom.id
        })

        procurement = self.env['procurement.order'].search(
            [('product_id', 'in',
              self.bom.bom_line_ids.mapped('product_id.id'))])

        self.assertEqual(len(procurement), 1)
        self.assertEqual(procurement.product_id.type, 'service')
