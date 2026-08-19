# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestMrpBomSaleMargin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bom_desk = cls.env.ref("mrp.mrp_bom_desk")  # [FURN_9666] Table
        cls.product_computer_desk = cls.env.ref(
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

    def test_02_cost_basis_direct_default(self):
        # Default cost basis is direct: BoM cost = sum of components only
        self.assertEqual(self.bom_desk.cost_basis, "direct")
        expected = sum(
            line.standard_price_subtotal for line in self.bom_desk.bom_line_ids
        ) / (self.bom_desk.product_qty or 1)
        self.assertAlmostEqual(self.bom_desk.standard_price, expected)

    def test_03_cost_basis_rolled_up_adds_operations(self):
        # Switching to rolled-up adds operation cost on top of components
        self.bom_desk.cost_basis = "rolled_up"
        qty = self.bom_desk.product_qty or 1
        components = sum(
            line.standard_price_subtotal for line in self.bom_desk.bom_line_ids
        )
        ops = self.bom_desk._get_operations_cost()
        self.assertAlmostEqual(self.bom_desk.standard_price, (components + ops) / qty)
        # Rolled-up batch cost reconciles with the displayed components + operations
        self.assertAlmostEqual(
            self.bom_desk._get_rolled_up_batch_cost(), components + ops
        )
