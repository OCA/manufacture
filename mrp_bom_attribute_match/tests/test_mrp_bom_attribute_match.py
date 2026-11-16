from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form

from .common import TestMrpBomAttributeMatchBase


class TestMrpBomAttributeMatch(TestMrpBomAttributeMatchBase):
    def test_bom_1(self):
        mrp_bom_form = Form(self.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = self.product_sword
        with mrp_bom_form.bom_line_ids.new() as line_form:
            line_form.product_id = self.product_plastic.product_variant_ids[0]
            line_form.component_template_id = self.product_plastic
            self.assertEqual(line_form.product_id.id, False)
            line_form.component_template_id = self.env["product.template"]
            self.assertEqual(
                line_form.product_id, self.product_plastic.product_variant_ids[0]
            )
            line_form.component_template_id = self.product_plastic
            line_form.product_qty = 1
            sword_cyan = self.sword_attrs.product_template_value_ids[0]
            with self.assertRaisesRegex(
                ValidationError,
                r"You cannot use an attribute value for attribute\(s\) .* in the "
                r"field “Apply on Variants” as it's the same attribute used in the "
                r"field “Match on Attribute” related to the component .*",
            ):
                line_form.bom_product_template_attribute_value_ids.add(sword_cyan)

    def test_bom_2(self):
        smell_attribute = self.env["product.attribute"].create(
            {"name": "Smell", "display_type": "radio", "create_variant": "always"}
        )
        orchid_attribute_value_id = self.env["product.attribute.value"].create(
            [
                {"name": "Orchid", "attribute_id": smell_attribute.id},
            ]
        )
        plastic_smells_like_orchid = self.env["product.template.attribute.line"].create(
            {
                "attribute_id": smell_attribute.id,
                "product_tmpl_id": self.product_plastic.id,
                "value_ids": [(4, orchid_attribute_value_id.id)],
            }
        )
        with self.assertRaisesRegex(
            UserError,
            r"This product template is used as a component in the BOMs for .* and "
            r"attribute\(s\) .* is not present in all such product\(s\), and this "
            r"would break the BOM behavior\.",
        ):
            vals = {
                "attribute_id": smell_attribute.id,
                "product_tmpl_id": self.product_plastic.id,
                "value_ids": [(4, orchid_attribute_value_id.id)],
            }
            self.product_plastic.write({"attribute_line_ids": [(Command.create(vals))]})
        mrp_bom_form = Form(self.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = self.product_sword
        with mrp_bom_form.bom_line_ids.new() as line_form:
            with self.assertRaisesRegex(
                UserError,
                r"Some attributes of the dynamic component are not included into "
                r"production product attributes\.",
            ):
                line_form.component_template_id = self.product_plastic
            line_form.component_template_id = self.env["product.template"]
            line_form.product_id = self.product_plastic.product_variant_ids[0]
        plastic_smells_like_orchid.unlink()

    def test_manufacturing_order_1(self):
        sword_cyan = self.product_sword.product_variant_ids[0]
        plastic_cyan = self.product_plastic.product_variant_ids[0]
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = sword_cyan
        mo_form.bom_id = self.bom_id
        mo_form.product_qty = 1
        self.mo_sword = mo_form.save()
        self.mo_sword.action_confirm()
        # Assert correct component variant was selected automatically
        self.assertEqual(
            self.mo_sword.move_raw_ids.product_id,
            plastic_cyan + self.product_9,
        )

    def test_manufacturing_order_2(self):
        # Delete Cyan value from plastic
        self.plastic_attrs.value_ids = [(3, self.plastic_attrs.value_ids[0].id, 0)]
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.product_sword.product_variant_ids.filtered(
            lambda x: x.display_name == "Plastic Sword (Cyan)"
        )
        mo_form.bom_id = self.bom_id
        mo_form.product_qty = 1
        self.mo_sword = mo_form.save()
        self.mo_sword.action_confirm()

    def test_manufacturing_order_3(self):
        # Delete attribute from sword
        self.product_sword.attribute_line_ids = [(5, 0, 0)]
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.product_sword.product_variant_ids[0]
        # Component skipped
        mo_form.bom_id = self.bom_id
        mo_form.product_qty = 1
        with self.assertRaisesRegex(
            ValidationError,
            r"Some attributes of the dynamic component are not included into .+",
        ):
            self.mo_sword = mo_form.save()

    def test_manufacturing_order_4(self):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.product_surf.product_variant_ids[0]
        mo_form.bom_id = self.surf_bom_id
        mo_form.product_qty = 1
        self.mo_sword = mo_form.save()
        self.mo_sword.action_confirm()

    # def test_manufacturing_order_5(self):
    #     mo_form = Form(self.env["mrp.production"])
    #     mo_form.product_id = self.product_surf.product_variant_ids[0]
    #     mo_form.bom_id = self.surf_wrong_bom_id
    #     mo_form.product_qty = 1
    #     self.mo_sword = mo_form.save()
    #     self.mo_sword.action_confirm()

    # def test_manufacturing_order_6(self):
    #     mo_form = Form(self.env["mrp.production"])
    #     mo_form.product_id = self.p1.product_variant_ids[0]
    #     mo_form.bom_id = self.p1_bom_id
    #     mo_form.product_qty = 1
    #     self.mo_sword = mo_form.save()
    #     self.mo_sword.action_confirm()

    def test_bom_recursion(self):
        test_bom_3 = self.env["mrp.bom"].create(
            {
                "product_id": self.product_9.id,
                "product_tmpl_id": self.product_9.product_tmpl_id.id,
                "product_uom_id": self.product_9.uom_id.id,
                "product_qty": 1.0,
                "consumption": "flexible",
                "type": "normal",
            }
        )
        test_bom_4 = self.env["mrp.bom"].create(
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
                "bom_id": test_bom_3.id,
                "product_id": self.product_10.id,
                "product_qty": 1.0,
            }
        )
        self.env["mrp.bom.line"].create(
            {
                "bom_id": test_bom_4.id,
                "product_id": self.product_9.id,
                "product_qty": 1.0,
            }
        )
        with self.assertRaisesRegex(UserError, r"Recursion error! .+"):
            test_bom_3.explode(self.product_9, 1)

    def test_mrp_report_bom_structure(self):
        sword_cyan = self.product_sword.product_variant_ids[0]
        BomStructureReport = self.env["report.mrp.report_bom_structure"]
        res = BomStructureReport._get_report_data(self.bom_id.id)
        self.assertTrue(res["is_variant_applied"])
        self.assertEqual(res["lines"]["product"], sword_cyan)
        product_l1 = self.env["product.product"].browse(
            res["lines"]["components"][0]["product_id"]
        )
        product_l2 = self.env["product.product"].browse(
            res["lines"]["components"][1]["product_id"]
        )
        self.assertEqual(
            product_l1.product_tmpl_id,
            self.bom_id.bom_line_ids[0].component_template_id,
        )
        self.assertEqual(
            product_l2,
            self.bom_id.bom_line_ids[1].product_id,
        )
        self.assertEqual(
            res["lines"]["components"][0]["parent_id"],
            self.bom_id.id,
        )

    def test_compute_bom_price_with_component_template_matching(self):
        sword_cyan = self.product_sword.product_variant_ids.filtered(
            lambda v: "Cyan" in v.display_name
        )
        self.assertTrue(sword_cyan, "Cyan sword variant should exist")

        # Set standard prices for components to make calculation predictable
        plastic_cyan = self.product_plastic.product_variant_ids.filtered(
            lambda v: "Cyan" in v.display_name
        )
        self.assertTrue(plastic_cyan, "Cyan plastic variant should exist")
        plastic_cyan.standard_price = 10.0
        self.product_9.standard_price = 5.0

        # Calculate BOM price for cyan sword
        bom_price = sword_cyan._compute_bom_price(self.bom_id)

        # Expected price should be:
        # - 1 * 10.0 (plastic component with matching attribute)
        # - 1 * 5.0 (regular component without template)
        expected_price = 15.0
        self.assertEqual(
            bom_price,
            expected_price,
            f"BOM price should be {expected_price}, got {bom_price}",
        )

    def test_compute_bom_price_line_product_none(self):
        # Create component with same attribute as sword but different values
        # This will pass the attribute check but fail the combination check
        component = self.env["product.template"].create(
            {
                "name": "Test Component",
                "is_storable": True,
            }
        )

        # Create a new attribute value that doesn't exist in sword
        red_value = self.env["product.attribute.value"].create(
            {"name": "Red", "attribute_id": self.product_attribute.id}
        )

        # Add the same attribute (Colour) to component but with Red value only
        self.env["product.template.attribute.line"].create(
            {
                "attribute_id": self.product_attribute.id,
                "product_tmpl_id": component.id,
                "value_ids": [Command.set([red_value.id])],
            }
        )

        # Create BOM with this component
        test_bom = self._create_bom(
            self.product_sword,
            [dict(component_template_id=component.id, product_qty=1)],
        )

        # Use cyan sword variant - this has Cyan attribute value
        sword_variant = self.product_sword.product_variant_ids.filtered(
            lambda v: "Cyan" in v.display_name
        )[0]

        # This should trigger len(combination) == 0 and return False
        bom_price = sword_variant._compute_bom_price(test_bom)

        # BOM price should be 0 since the component line is ignored
        self.assertEqual(bom_price, 0.0)

    def test_explode_nested_kit_rounding(self):
        """The quantity of a nested kit is not rounded before exploding it"""
        fns, cmp1, cmp2 = self.env["product.product"].create(
            [{"name": "FNS"}, {"name": "CMP1"}, {"name": "CMP2"}]
        )
        self.env.ref("uom.product_uom_unit").rounding = 0.01
        fns_bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": fns.product_tmpl_id.id,
                "type": "phantom",
                "bom_line_ids": [
                    Command.create({"product_id": cmp1.id, "product_qty": 10})
                ],
            }
        )
        self.env["mrp.bom"].create(
            {
                "product_tmpl_id": cmp1.product_tmpl_id.id,
                "product_qty": 5000,
                "type": "phantom",
                "bom_line_ids": [
                    Command.create({"product_id": cmp2.id, "product_qty": 50})
                ],
            }
        )
        # 1 FNS = 10 CMP1 = 0.10 CMP2 (50 / 5000 * 10)
        _boms, lines = fns_bom.explode(fns, 1)
        self.assertEqual(lines[0][1]["qty"], 0.10)

    def test_explode_nested_kit_sequence(self):
        """The components of a nested kit keep the place of the kit line"""
        product, comp1, kit, kit_comp1, kit_comp2, comp3 = self.env[
            "product.product"
        ].create(
            [
                {"name": "Product"},
                {"name": "Component 1"},
                {"name": "Kit"},
                {"name": "Kit component 1"},
                {"name": "Kit component 2"},
                {"name": "Component 3"},
            ]
        )
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "bom_line_ids": [
                    Command.create({"product_id": comp1.id, "sequence": 1}),
                    Command.create({"product_id": kit.id, "sequence": 2}),
                    Command.create({"product_id": comp3.id, "sequence": 3}),
                ],
            }
        )
        self.env["mrp.bom"].create(
            {
                "product_tmpl_id": kit.product_tmpl_id.id,
                "type": "phantom",
                "bom_line_ids": [
                    Command.create({"product_id": kit_comp1.id}),
                    Command.create({"product_id": kit_comp2.id}),
                ],
            }
        )
        _boms, lines = bom.explode(product, 1)
        self.assertEqual(
            [line.product_id for line, _vals in lines],
            [comp1, kit_comp1, kit_comp2, comp3],
        )
