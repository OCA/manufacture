# -*- coding: utf-8 -*-
# (c) 2015 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestMrpProductionManualClose(common.TransactionCase):

    def setUp(self):
        super(TestMrpProductionManualClose, self).setUp()
        self.product = self.env['product.product'].create({'name': 'Test'})
        self.bom = self.env['mrp.bom'].create(
            {'product_id': self.product.id,
             'product_tmpl_id': self.product.product_tmpl_id.id,
             'product_qty': 2,
             })
        self.production_model = self.env['mrp.production']
        self.production_wiz = self.env['mrp.product.produce']
        self.production = self.env['mrp.production'].create(
            {'product_id': self.product.id,
             'product_uom': self.env.ref('product.product_uom_unit').id,
             'bom_id': self.bom.id,
             })

    def test_production_close(self):
        self.production.signal_workflow('button_confirm')
        self.production.force_production()
        self.production.signal_workflow('moves_ready')
        self.wiz = self.production_wiz.with_context(
            active_id=self.production.id).create(
                {'product_id': self.product.id,
                 'product_qty': 2,
                 })
        self.wiz.with_context(active_id=self.production.id).do_produce()
        self.assertEqual(self.production.state, 'in_production',
                         'Error work center line not in in_production state')
        self.production.button_produce_close()
        self.assertEqual(self.production.state, 'done',
                         'Error work center line not in done state')
