# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import TransactionCase


class TestProduct(TransactionCase):

    def test_action_view_bom(self):
        # Covering test
        p1 = self.env['product.product'].create({'name': 'Test P1'})
        result = p1.action_view_bom()
        self.assertIn(('dismantling', '=', False), result['domain'])
