# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

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

    def test_bom_cost_template_skip_and_ignore(self):
        sword_cyan, _ = self.product_sword.product_variant_ids
        plastic_cyan, _ = self.product_plastic.product_variant_ids
        plastic_cyan.standard_price = 1.00

        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product_sword.id,
                "type": "normal",
            }
        )
        self.env["mrp.bom.line"].create(
            {
                "bom_id": bom.id,
                "product_id": plastic_cyan.id,
                "product_qty": 1.0,
                "component_template_id": self.product_plastic.id,
            }
        )
        self.env["mrp.bom.line"].create(
            {
                "bom_id": bom.id,
                "product_id": plastic_cyan.id,
                "product_qty": 1.0,
                "component_template_id": self.product_plastic.id,
            }
        )

        skip_bom_line_iter = iter([True, False])
        get_component_template_product_iter = iter([None])

        def skip_bom_line_side_effect(_):
            return next(skip_bom_line_iter, False)

        def get_component_template_product_side_effect(_, __, product_id):
            return next(get_component_template_product_iter, product_id)

        with patch.object(
            type(bom.bom_line_ids[0]),
            "_skip_bom_line",
            side_effect=skip_bom_line_side_effect,
        ):
            with patch.object(
                type(bom),
                "_get_component_template_product",
                side_effect=get_component_template_product_side_effect,
            ):
                sword_cyan._compute_bom_price(bom)

        self.assertEqual(sword_cyan.standard_price, 0.0)
