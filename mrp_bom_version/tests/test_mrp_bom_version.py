# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestMrpBomVersion(common.TransactionCase):

    def setUp(self):
        super(TestMrpBomVersion, self).setUp()
        self.parameter_model = self.env['ir.config_parameter']
        self.bom_model = self.env['mrp.bom'].with_context(
            test_mrp_bom_version=True)
        self.company = self.env.ref('base.main_company')
        vals = {
            'company_id': self.company.id,
            'product_tmpl_id':
                self.env.ref('product.product_product_11_product_template').id,
            'bom_line_ids':
                [(0, 0, {'product_id':
                         self.env.ref('product.product_product_5').id}),
                 (0, 0, {'product_id':
                         self.env.ref('product.product_product_6').id})],
        }
        self.mrp_bom = self.bom_model.create(vals)

    def test_mrp_bom(self):
        self.assertEqual(
            self.mrp_bom.state, 'draft', "New BoM must be in state 'draft'")
        self.assertEqual(
            self.mrp_bom.version, 1, 'Incorrect version for new BoM')
        self.assertFalse(
            self.mrp_bom.active, 'New BoMs must be created inactive')
        self.mrp_bom.button_activate()
        self.assertTrue(
            self.mrp_bom.active, 'Incorrect activation, check must be True')
        self.assertEqual(
            self.mrp_bom.state, 'active',
            "Incorrect state, it should be 'active'")
        self.mrp_bom.button_historical()
        self.assertFalse(
            self.mrp_bom.active, 'Check must be False, after historification')
        self.assertEqual(
            self.mrp_bom.state, 'historical',
            "Incorrect state, it should be 'historical'")

    def test_mrp_bom_back2draft_default(self):
        self.mrp_bom.button_activate()
        self.mrp_bom.button_draft()
        self.assertFalse(
            self.mrp_bom.active, 'Check must be False')

    def test_mrp_bom_back2draft_active(self):
        self.parameter_model.create({'key': 'active.draft', 'value': True})
        self.mrp_bom.button_activate()
        self.mrp_bom.button_draft()
        self.assertTrue(
            self.mrp_bom.active, 'Check must be True, as set in parameters')

    def test_mrp_bom_versioning(self):
        self.mrp_bom.button_activate()
        self.mrp_bom.button_new_version()
        self.assertFalse(
            self.mrp_bom.active,
            'Check must be False, it must have been historified')
        self.assertEqual(
            self.mrp_bom.state, 'historical',
            'Incorrect state, it must have been historified')
        new_boms = self.bom_model.search(
            [('parent_bom', '=', self.mrp_bom.id)])
        for new_bom in new_boms:
            self.assertEqual(
                new_bom.version, self.mrp_bom.version + 1,
                'New BoM version must be +1 from origin BoM version')
            self.assertEqual(
                new_bom.active,
                self.parameter_model.search(
                    [('key', '=', 'active.draft')]).value,
                'It does not match active draft check state set in company')
            self.assertEqual(
                new_bom.state, 'draft',
                "New version must be created in 'draft' state")
