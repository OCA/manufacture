# Copyright 2026 CHEF PIXEL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form

from .common import TestMrpBomAttributeMatchBase


class TestMrpBomAttributeMatch(TestMrpBomAttributeMatchBase):
    # ---------------------------------------------------------
    # BOM FORM TESTS
    # ---------------------------------------------------------

    def test_bom_1(self):
        mrp_bom_form = Form(self.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = self.product_sword

        with mrp_bom_form.bom_line_ids.new() as line_form:
            line_form.product_id = self.product_plastic.product_variant_id
            line_form.component_template_id = self.product_plastic

            self.assertFalse(line_form.product_id)

            line_form.component_template_id = self.env["product.template"]
            self.assertEqual(
                line_form.product_id,
                self.product_plastic.product_variant_id,
            )

            line_form.component_template_id = self.product_plastic
            line_form.product_qty = 1

            sword_cyan = self.sword_attrs.product_template_value_ids[0]

            with self.assertRaisesRegex(
                ValidationError,
                r"You cannot use an attribute value",
            ):
                line_form.bom_product_template_attribute_value_ids.add(sword_cyan)

    def test_bom_2(self):
        smell_attribute = self.env["product.attribute"].create(
            {
                "name": "Smell",
                "display_type": "radio",
                "create_variant": "always",
            }
        )

        orchid_value = self.env["product.attribute.value"].create(
            {
                "name": "Orchid",
                "attribute_id": smell_attribute.id,
            }
        )

        with self.assertRaisesRegex(
            UserError,
            r"This product template is used as a component",
        ):
            self.product_plastic.write(
                {
                    "attribute_line_ids": [
                        Command.create(
                            {
                                "attribute_id": smell_attribute.id,
                                "value_ids": [Command.set([orchid_value.id])],
                            }
                        )
                    ]
                }
            )

    # ---------------------------------------------------------
    # MANUFACTURING ORDER TESTS
    # ---------------------------------------------------------

    def test_manufacturing_order_1(self):
        sword_cyan = self.product_sword.product_variant_id
        plastic_cyan = self.product_plastic.product_variant_id

        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = sword_cyan
        mo_form.bom_id = self.bom_id
        mo_form.product_qty = 1

        mo = mo_form.save()
        mo.action_confirm()

        self.assertIn(plastic_cyan, mo.move_raw_ids.mapped("product_id"))

    def test_manufacturing_order_4(self):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.product_surf.product_variant_id
        mo_form.bom_id = self.surf_bom_id
        mo_form.product_qty = 1

        mo = mo_form.save()
        mo.action_confirm()
        self.assertEqual(mo.state, "confirmed")

    # ---------------------------------------------------------
    # REPORT TEST
    # ---------------------------------------------------------

    def test_mrp_report_bom_structure(self):
        report = self.env["report.mrp.report_bom_structure"]
        sword_variant = self.product_sword.product_variant_id

        res = report._get_report_data(self.bom_id.id, variant_id=sword_variant.id)

        self.assertTrue(
            res.get("is_variant_applied"), "Flag 'is_variant_applied' should be True"
        )

        # Handle various return formats for the product record
        root_product = res.get("product")
        root_id = (
            root_product.id if hasattr(root_product, "id") else res.get("product_id")
        )

        self.assertEqual(root_id, sword_variant.id)

    # ---------------------------------------------------------
    # BOM PRICE COMPUTATION
    # ---------------------------------------------------------

    def test_compute_bom_price_with_component_template_matching(self):
        sword_variant = self.product_sword.product_variant_id
        plastic_variant = self.product_plastic.product_variant_id

        plastic_variant.standard_price = 10.0
        self.product_9.standard_price = 5.0

        price = sword_variant._compute_bom_price(self.bom_id)

        self.assertEqual(price, 15.0)
