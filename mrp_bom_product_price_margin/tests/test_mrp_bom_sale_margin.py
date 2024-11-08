# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestMrpBomSaleMargin(TransactionCase):
    def setUp(self):
        super(TestMrpBomSaleMargin, self).setUp()
        self.bom_desk = self.env.ref("mrp.mrp_bom_desk")  # [FURN_9666] Table
        self.product_computer_desk = self.env.ref(
            "mrp.product_product_computer_desk_product_template"
        )

    def test_01_bom_product_product_set_cost(self):
        # Set product product
        self.bom_desk.product_tmpl_id = self.product_computer_desk
        self.assertNotEqual(
            self.bom_desk.standard_price,
            self.bom_desk.product_tmpl_id.standard_price,
        )
        self.assertNotEqual(
            self.bom_desk.diff_product_bom_standard_price,
            False,
        )
        # Set product product standard price based on bom
        self.bom_desk.set_product_standard_price()
        self.assertEqual(
            self.bom_desk.diff_product_bom_standard_price,
            False,
        )
        self.assertEqual(
            self.bom_desk.standard_price,
            self.bom_desk.product_tmpl_id.standard_price,
        )
