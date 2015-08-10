# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
import openerp.tests.common as common


class TestMrpBomVersion(common.TransactionCase):

    def setUp(self):
        super(TestMrpBomVersion, self).setUp()
        self.mrp_bom_model = self.env['mrp.bom']
        vals = {"product_tmpl_id":
                self.env.ref('product.product_product_11_product_template').id,
                "active": True,
                "bom_line_ids":
                [(0, 0, {'product_id':
                         self.env.ref('product.product_product_5').id}),
                 (0, 0, {'product_id':
                         self.env.ref('product.product_product_6').id})],
                }
        self.new_mrp_bom = self.mrp_bom_model.create(vals)

    def test_mrp_bom_version(self):
        self.assertEqual(self.new_mrp_bom.state, 'draft',
                         "No 'draft' state for MRP new BoM")
        self.assertEqual(self.new_mrp_bom.version, 1,
                         "Incorrect version for MRP new BoM")
        self.new_mrp_bom.button_activate()
        self.assertEqual(self.new_mrp_bom.active, True,
                         "Incorrect active field for MRP new BoM, after"
                         " activation")
        self.assertEqual(self.new_mrp_bom.state, 'active',
                         "No 'active' state for MRP new BoM, after activation")
        self.new_mrp_bom.button_historical()
        self.assertEqual(self.new_mrp_bom.active, False,
                         "Incorrect active field for MRP new BoM, after"
                         " historification")
        self.assertEqual(self.new_mrp_bom.state, 'historical',
                         "No 'historical' state for MRP new BoM, after"
                         " activation")
