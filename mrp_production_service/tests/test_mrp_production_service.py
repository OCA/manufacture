# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestMrpProductionService(TransactionCase):
    def setUp(self):
        super(TestMrpProductionService, self).setUp()

        # Create products
        self.obj_warehouse = self.env['stock.warehouse']
        self.test_wh = self.obj_warehouse.create({
            'name': 'Test WH',
            'code': 'T',
        })
        self.supplier = self.env['res.partner'].create({
            'name': 'Supplier',
            'supplier': True,
        })
        self.product_model = self.env['product.product']
        self.p1 = self.product_model.create({
            'name': '101',
            'type': 'product',
        })
        self.service = self.product_model.create({
            'name': 'Galvanize Service',
            'type': 'service',
            'seller_ids': [(0, 0, {
                'name': self.supplier.id,
                'price': 100.0,
            })]
        })
        self.service.property_subcontracted_service = True
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

        procurement = self.env['purchase.order.line'].search(
            [('product_id', 'in',
              self.bom.bom_line_ids.mapped('product_id.id'))])

        self.assertEqual(len(procurement), 1)
        self.assertEqual(procurement.product_id.type, 'service')
