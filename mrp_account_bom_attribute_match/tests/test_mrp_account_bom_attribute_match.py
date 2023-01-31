# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.mrp_bom_attribute_match.tests.common import (
    TestMrpBomAttributeMatchBase,
)


class TestMrpAccount(TestMrpBomAttributeMatchBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_bom_cost(self):
        sword_cyan, sword_magenta = self.product_sword.product_variant_ids
        plastic_cyan, plastic_magenta = self.product_plastic.product_variant_ids
        plastic_cyan.standard_price = 1.00
        plastic_magenta.standard_price = 2.00
        sword_cyan.button_bom_cost()
        sword_magenta.button_bom_cost()
        self.assertEqual(sword_cyan.standard_price, 1.00)
        self.assertEqual(sword_magenta.standard_price, 2.00)
