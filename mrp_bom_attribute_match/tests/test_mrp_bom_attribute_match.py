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

    def test_check_product_with_component_change_allowed(self):
        # The sword BoM has a line with component_template_id=product_plastic,
        # which carries the "Colour" attribute. That attribute is therefore
        # present in match_on_attribute_ids of the bom line and must remain on
        # the sword template. Replacing it with another attribute (so the
        # template still has attributes, just not Colour) must raise.
        bom_line = self.bom_id.bom_line_ids.filtered("match_on_attribute_ids")
        self.assertTrue(bom_line)
        self.assertIn(self.product_attribute, bom_line.match_on_attribute_ids)
        other_attr = self.env["product.attribute"].create(
            {"name": "Shape", "display_type": "radio", "create_variant": "always"}
        )
        self.env["product.attribute.value"].create(
            [
                {"name": "Round", "attribute_id": other_attr.id},
                {"name": "Square", "attribute_id": other_attr.id},
            ]
        )
        with self.assertRaisesRegex(
            UserError,
            r"The attributes you're trying to remove are used in the BoM as a "
            r"match with Component \(Product Template\)\.",
        ):
            self.product_sword.write(
                {
                    "attribute_line_ids": [
                        Command.delete(self.sword_attrs.id),
                        Command.create(
                            {
                                "attribute_id": other_attr.id,
                                "value_ids": [Command.set(other_attr.value_ids.ids)],
                            }
                        ),
                    ]
                }
            )

    def test_check_product_with_component_change_allowed_no_variant(self):
        # Attributes with create_variant == "no_variant" are ignored by the
        # constraint: removing such an attribute from the product template
        # must not raise even when present on a component template.
        no_variant_attr = self.env["product.attribute"].create(
            {
                "name": "Size",
                "display_type": "radio",
                "create_variant": "no_variant",
            }
        )
        self.env["product.attribute.value"].create(
            [
                {"name": "S", "attribute_id": no_variant_attr.id},
                {"name": "M", "attribute_id": no_variant_attr.id},
            ]
        )
        size_line = self.env["product.template.attribute.line"].create(
            {
                "attribute_id": no_variant_attr.id,
                "product_tmpl_id": self.product_sword.id,
                "value_ids": [Command.set(no_variant_attr.value_ids.ids)],
            }
        )
        # Removing the no_variant attribute line from sword should succeed
        # (no UserError from _check_product_with_component_change_allowed).
        size_line.unlink()
        self.assertNotIn(
            no_variant_attr, self.product_sword.attribute_line_ids.attribute_id
        )

    def test_component_resolution_ignores_archived_ptav(self):
        # Regression: an attribute value archived on the component template
        # (ptav_active=False) must not break the component resolution.
        #
        # The product (sword) and the component (plastic) both carry a second
        # attribute "Material" with a shared value "Wood". A variant is created
        # so the value cannot be deleted, then the value is removed from the
        # component: this archives the component ptav instead of deleting it.
        # Since ptav_active is not the magic `active` field, a plain search
        # would still return that archived ptav and build an impossible
        # combination, wrongly discarding the component.
        material = self.env["product.attribute"].create(
            {"name": "Material", "display_type": "radio", "create_variant": "always"}
        )
        wood, steel = self.env["product.attribute.value"].create(
            [
                {"name": "Wood", "attribute_id": material.id},
                {"name": "Steel", "attribute_id": material.id},
            ]
        )
        # Add Material to both product and component templates.
        self.env["product.template.attribute.line"].create(
            {
                "attribute_id": material.id,
                "product_tmpl_id": self.product_sword.id,
                "value_ids": [Command.set((wood + steel).ids)],
            }
        )
        plastic_material_line = self.env["product.template.attribute.line"].create(
            {
                "attribute_id": material.id,
                "product_tmpl_id": self.product_plastic.id,
                "value_ids": [Command.set((wood + steel).ids)],
            }
        )
        # Reference a plastic variant carrying "Wood" so the ptav cannot be
        # deleted and is archived instead when the value is removed. A stock lot
        # is used because a variant with lots is kept (archived) rather than
        # unlinked (see product.product._filter_to_unlink); this module weakens
        # mrp.bom.line.product_id to ondelete="set null", so a BoM reference
        # would no longer block the deletion.
        self.product_plastic.tracking = "lot"
        plastic_ptav_wood = plastic_material_line.product_template_value_ids.filtered(
            lambda ptav: ptav.product_attribute_value_id == wood
        )
        plastic_wood_variant = self.product_plastic.product_variant_ids.filtered(
            lambda v: plastic_ptav_wood in v.product_template_attribute_value_ids
        )[:1]
        self.assertTrue(
            plastic_wood_variant,
            "Precondition: a plastic variant carrying 'Wood' should exist",
        )
        self.env["stock.lot"].create(
            {
                "name": "LOT-WOOD-0001",
                "product_id": plastic_wood_variant.id,
            }
        )
        # Remove Material from the component template only: this archives the
        # ptavs (they are referenced by the kept variant) rather than deleting
        # them.
        self.product_plastic.write(
            {"attribute_line_ids": [Command.delete(plastic_material_line.id)]}
        )
        archived = self.env["product.template.attribute.value"].search(
            [
                ("product_tmpl_id", "=", self.product_plastic.id),
                ("attribute_id", "=", material.id),
                ("ptav_active", "=", False),
            ]
        )
        self.assertTrue(
            archived, "Precondition: component Material ptav should be archived"
        )
        # Produce the "Wood" sword: the component must still resolve to a plastic
        # variant matching only on Colour, ignoring the archived Material ptav.
        sword_wood_cyan = self.product_sword.product_variant_ids.filtered(
            lambda v: v.product_template_attribute_value_ids.filtered(
                lambda ptav: ptav.product_attribute_value_id == wood
            )
            and v.product_template_attribute_value_ids.filtered(
                lambda ptav: ptav.product_attribute_value_id
                == self.attribute_value_ids[0]
            )
        )[:1]
        self.assertTrue(sword_wood_cyan)
        bom_line = self.bom_id.bom_line_ids.filtered("component_template_id")
        resolved = self.bom_id._get_component_template_product(
            bom_line, sword_wood_cyan, bom_line.product_id
        )
        self.assertTrue(
            resolved,
            "Component should resolve despite the archived Material ptav",
        )
        self.assertEqual(resolved.product_tmpl_id, self.product_plastic)
        self.assertIn(
            self.attribute_value_ids[0],
            resolved.product_template_attribute_value_ids.product_attribute_value_id,
        )

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
