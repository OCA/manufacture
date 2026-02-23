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

        plastic_line = self.env["product.template.attribute.line"].create(
            {
                "attribute_id": smell_attribute.id,
                "product_tmpl_id": self.product_plastic.id,
                "value_ids": [Command.set([orchid_value.id])],
            }
        )

        with self.assertRaisesRegex(
            UserError,
            r"This product template is used as a component",
        ):
            vals = {
                "attribute_id": smell_attribute.id,
                "product_tmpl_id": self.product_plastic.id,
                "value_ids": [Command.set([orchid_value.id])],
            }
            self.product_plastic.write({"attribute_line_ids": [Command.create(vals)]})

        mrp_bom_form = Form(self.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = self.product_sword

        with mrp_bom_form.bom_line_ids.new() as line_form:
            with self.assertRaisesRegex(
                UserError,
                r"Some attributes of the dynamic component",
            ):
                line_form.component_template_id = self.product_plastic

            line_form.component_template_id = self.env["product.template"]
            line_form.product_id = self.product_plastic.product_variant_id

        plastic_line.unlink()

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

        self.assertEqual(
            mo.move_raw_ids.product_id,
            plastic_cyan + self.product_9,
        )

    def test_manufacturing_order_2(self):
        self.plastic_attrs.value_ids = [(3, self.plastic_attrs.value_ids[0].id, 0)]

        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.product_sword.product_variant_id
        mo_form.bom_id = self.bom_id
        mo_form.product_qty = 1

        mo = mo_form.save()
        mo.action_confirm()

    def test_manufacturing_order_3(self):
        self.product_sword.attribute_line_ids = [(5, 0, 0)]

        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.product_sword.product_variant_id
        mo_form.bom_id = self.bom_id
        mo_form.product_qty = 1

        with self.assertRaisesRegex(
            ValidationError,
            r"Some attributes of the dynamic component",
        ):
            mo_form.save()

    def test_manufacturing_order_4(self):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.product_surf.product_variant_id
        mo_form.bom_id = self.surf_bom_id
        mo_form.product_qty = 1

        mo = mo_form.save()
        mo.action_confirm()

    # ---------------------------------------------------------
    # RECURSION
    # ---------------------------------------------------------

    def test_bom_recursion(self):
        bom3 = self.env["mrp.bom"].create(
            {
                "product_id": self.product_9.id,
                "product_tmpl_id": self.product_9.product_tmpl_id.id,
                "product_uom_id": self.product_9.uom_id.id,
                "product_qty": 1.0,
                "consumption": "flexible",
                "type": "normal",
            }
        )

        bom4 = self.env["mrp.bom"].create(
            {
                "product_id": self.product_10.id,
                "product_tmpl_id": self.product_10.product_tmpl_id.id,
                "product_uom_id": self.product_10.uom_id.id,
                "product_qty": 1.0,
                "consumption": "flexible",
                "type": "phantom",
            }
        )

        self.env["mrp.bom.line"].create(
            {
                "bom_id": bom3.id,
                "product_id": self.product_10.id,
                "product_qty": 1.0,
            }
        )

        self.env["mrp.bom.line"].create(
            {
                "bom_id": bom4.id,
                "product_id": self.product_9.id,
                "product_qty": 1.0,
            }
        )

        with self.assertRaisesRegex(UserError, r"Recursion error"):
            bom3.explode(self.product_9, 1.0)

    # ---------------------------------------------------------
    # REPORT TEST
    # ---------------------------------------------------------

    def test_mrp_report_bom_structure(self):
        report = self.env["report.mrp.report_bom_structure"]
        res = report._get_report_data(self.bom_id.id)

        self.assertTrue(res["is_variant_applied"])
        self.assertEqual(
            res["lines"]["product"],
            self.product_sword.product_variant_id,
        )

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

    def test_compute_bom_price_line_product_none(self):
        component = self.env["product.template"].create(
            {
                "name": "Test Component",
                "detailed_type": "product",  # Changed for Odoo 19
            }
        )

        red_value = self.env["product.attribute.value"].create(
            {
                "name": "Red",
                "attribute_id": self.product_attribute.id,
            }
        )

        self.env["product.template.attribute.line"].create(
            {
                "attribute_id": self.product_attribute.id,
                "product_tmpl_id": component.id,
                "value_ids": [Command.set([red_value.id])],
            }
        )

        test_bom = self._create_bom(
            self.product_sword,
            [dict(component_template_id=component.id, product_qty=1)],
        )

        sword_variant = self.product_sword.product_variant_id
        price = sword_variant._compute_bom_price(test_bom)

        self.assertEqual(price, 0.0)
