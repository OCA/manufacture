# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestMrpBomLineNetQty(TransactionCase):
    def setUp(self):
        super(TestMrpBomLineNetQty, self).setUp()
        self.bom_desk_combination = self.env.ref("mrp.mrp_bom_manufacture")

    def test_01_calculate_qty_net(self):
        bom_line_0 = self.bom_desk_combination.bom_line_ids[0]
        self.assertNotEqual(bom_line_0.product_qty, bom_line_0.product_qty_net)
        # Trigger onchange to get produt_qty_net
        bom_line_0._onchange_product_qty()
        self.assertEqual(bom_line_0.product_qty, bom_line_0.product_qty_net)

    def test_02_change_gross_qty_onchange_net(self):
        bom_line_0 = self.bom_desk_combination.bom_line_ids[0]
        bom_line_0.product_qty = 10
        # Trigger onchange to get produt_qty_net
        bom_line_0._onchange_product_qty()
        self.assertEqual(bom_line_0.product_qty, bom_line_0.product_qty_net)

    def test_03_change_qty_check_diff(self):
        bom_line_0 = self.bom_desk_combination.bom_line_ids[0]
        # Trigger onchange to get produt_qty_net
        bom_line_0._onchange_product_qty()
        self.assertEqual(bom_line_0.diff_product_qty_gross_net, 0)
        bom_line_0.product_qty_net = bom_line_0.product_qty + 10
        self.assertNotEqual(bom_line_0.diff_product_qty_gross_net, 0)

    def test_04_change_loss_check_button_calculate_net(self):
        bom_line_0 = self.bom_desk_combination.bom_line_ids[0]
        bom_line_0.product_qty = 100
        bom_line_0.loss_percentage = 10
        # Trigger onchange to get produt_qty_net
        bom_line_0._onchange_product_qty()
        self.assertNotEqual(90, bom_line_0.product_qty_net)
        # Trigger button to set produt_qty_net
        bom_line_0.set_product_qty_net()
        self.assertEqual(90, bom_line_0.product_qty_net)

    def test_05_change_loss_check_button_calculate_gross(self):
        bom_line_0 = self.bom_desk_combination.bom_line_ids[0]
        bom_line_0.product_qty_net = 90
        bom_line_0.loss_percentage = 10
        self.assertNotEqual(100, bom_line_0.product_qty)
        # Trigger button to set produt_qty_net
        bom_line_0.set_product_qty_gross()
        self.assertEqual(100, bom_line_0.product_qty)
