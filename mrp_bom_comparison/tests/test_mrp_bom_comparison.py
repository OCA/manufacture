# -*- coding: utf-8 -*-
# Copyright 2018 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestMrpBomComparison(TestMrpCommon):

    def setUp(self):
        super(TestMrpBomComparison, self).setUp()
        # bom_3 (product_6) -> bom_2 (product_5) -> bom_1 (product_4)
        self.wiz_model = self.env['wizard.mrp.bom.comparison']
        self.product_1.default_code = u"P1"
        self.product_2.default_code = u"P2"
        self.product_3.default_code = u"P3"
        self.product_4.default_code = u"P4-BOM_1"
        self.product_5.default_code = u"P5-BOM_2"
        self.product_6.default_code = u"P6-BOM_3"

        # Create a 'new_bom_1' from 'bom_1'
        self.new_product_4 = self.product_4.copy(
            {'default_code': u"P4-NEW_BOM_1"})
        self.new_bom_1 = self.bom_1.copy({
            'product_id': self.new_product_4.id,
            'product_tmpl_id': self.new_product_4.product_tmpl_id.id,
        })
        # Change a component qty on 'new_bom_1':
        #   product_2: 2 => 1
        self.new_bom_1.bom_line_ids.filtered(
            lambda l: l.product_id == self.product_2).product_qty = 1

        # Create a 'new_bom_2' from 'bom_2'
        self.new_product_5 = self.product_5.copy(
            {'default_code': u"P5-NEW_BOM_2"})
        self.new_bom_2 = self.bom_2.copy({
            'product_id': self.new_product_5.id,
            'product_tmpl_id': self.new_product_5.product_tmpl_id.id,
        })
        self.new_bom_2.bom_line_ids.filtered(
            lambda l: l.product_id == self.product_4).write(
                {'product_id': self.new_product_4.id})
        # Change a component qty on 'new_bom_2':
        #   product_3:      3 => 4
        #   new_product_4:  2 => 6
        self.new_bom_2.bom_line_ids.filtered(
            lambda l: l.product_id == self.product_3).product_qty = 4
        self.new_bom_2.bom_line_ids.filtered(
            lambda l: l.product_id == self.new_product_4).product_qty = 6

        # Create a 'new_bom_3' from 'bom_3'
        self.new_bom_3 = self.bom_3.copy()
        self.new_bom_3.bom_line_ids.filtered(
            lambda l: l.product_id == self.product_4).write(
                {'product_id': self.new_product_4.id})
        self.new_bom_3.bom_line_ids.filtered(
            lambda l: l.product_id == self.product_5).write(
                {'product_id': self.new_product_5.id})
        # Change a component qty on 'new_bom_3':
        #   product_2:      12 => 10
        self.new_bom_3.bom_line_ids.filtered(
            lambda l: l.product_id == self.product_2).product_qty = 10

        # Make a comparison between the original BoM and the new one
        vals = {
            'bom1_id': self.bom_3.id,
            'bom2_id': self.new_bom_3.id,
        }
        self.wiz = self.wiz_model.create(vals)
        self.wiz.run()

    def test_line_changed_ids(self):
        self.assertTrue(self.wiz.line_changed_ids)
        self.assertEqual(len(self.wiz.line_changed_ids), 3)
        changed_products = self.wiz.line_changed_ids.mapped('product_id')
        self.assertIn(self.product_1, changed_products)
        self.assertIn(self.product_2, changed_products)
        self.assertIn(self.product_3, changed_products)
        # product_1 qty:
        #   v1: 8*4/4 + 2*2*4/4 = 12
        #   v2: 8*4/4 + 2*6*4/4 = 20
        #   diff = +8
        line_product_1 = self.wiz.line_changed_ids.filtered(
            lambda l: l.product_id == self.product_1)
        self.assertEqual(line_product_1.diff_qty, 8)
        # product_2 qty:
        #   v1: 12 + 8*2/4 + 2*2*2/4 = 18
        #   v2: 10 + 8*1/4 + 2*6*1/4 = 15
        #   diff = -3
        line_product_2 = self.wiz.line_changed_ids.filtered(
            lambda l: l.product_id == self.product_2)
        self.assertEqual(line_product_2.diff_qty, -3)
        # product_3 qty:
        #   v1: 2*3 = 6
        #   v2: 2*4 = 8
        #   diff = +2
        line_product_3 = self.wiz.line_changed_ids.filtered(
            lambda l: l.product_id == self.product_3)
        self.assertEqual(line_product_3.diff_qty, 2)

    def test_line_added_ids(self):
        self.assertTrue(self.wiz.line_added_ids)
        self.assertEqual(len(self.wiz.line_added_ids), 2)
        added_products = self.wiz.line_added_ids.mapped('product_id')
        self.assertIn(self.new_product_4, added_products)
        self.assertIn(self.new_product_5, added_products)
        # new_product4 qty:
        #   v1: 0
        #   v2: 8 + 2*6 = 20
        #   diff = +20
        line_new_product_4 = self.wiz.line_added_ids.filtered(
            lambda l: l.product_id == self.new_product_4)
        self.assertEqual(line_new_product_4.diff_qty, 20)
        # new_product5 qty:
        #   v1: 0
        #   v2: 2
        #   diff = +2
        line_new_product_5 = self.wiz.line_added_ids.filtered(
            lambda l: l.product_id == self.new_product_5)
        self.assertEqual(line_new_product_5.diff_qty, 2)

    def test_line_removed_ids(self):
        self.assertTrue(self.wiz.line_removed_ids)
        self.assertEqual(len(self.wiz.line_removed_ids), 2)
        removed_products = self.wiz.line_removed_ids.mapped('product_id')
        self.assertIn(self.product_4, removed_products)
        self.assertIn(self.product_5, removed_products)
        # product4 qty:
        #   v1: 12
        #   v2: 0
        #   diff = -12
        line_product_4 = self.wiz.line_removed_ids.filtered(
            lambda l: l.product_id == self.product_4)
        self.assertEqual(line_product_4.diff_qty, -12)
        # product5 qty:
        #   v1: 2
        #   v2: 0
        #   diff = -2
        line_product_5 = self.wiz.line_removed_ids.filtered(
            lambda l: l.product_id == self.product_5)
        self.assertEqual(line_product_5.diff_qty, -2)
