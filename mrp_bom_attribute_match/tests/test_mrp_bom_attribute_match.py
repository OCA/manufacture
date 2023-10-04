from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form

from .common import TestMrpBomAttributeMatchBase


class TestMrpAttachmentMgmt(TestMrpBomAttributeMatchBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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
            with self.assertRaises(ValidationError):
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
        with self.assertRaises(UserError):
            vals = {
                "attribute_id": smell_attribute.id,
                "product_tmpl_id": self.product_plastic.id,
                "value_ids": [(4, orchid_attribute_value_id.id)],
            }
            self.product_plastic.write({"attribute_line_ids": [(0, 0, vals)]})
        mrp_bom_form = Form(self.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = self.product_sword
        with mrp_bom_form.bom_line_ids.new() as line_form:
            with self.assertRaises(ValidationError):
                line_form.component_template_id = self.product_plastic
        plastic_smells_like_orchid.unlink()

    def test_manufacturing_order_1(self):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.product_sword.product_variant_ids.filtered(
            lambda x: x.display_name == "Plastic Sword (Cyan)"
        )
        mo_form.bom_id = self.bom_id
        mo_form.product_qty = 1
        self.mo_sword = mo_form.save()
        self.mo_sword.action_confirm()
        # Assert correct component variant was selected automatically
        self.assertEqual(
            self.mo_sword.move_raw_ids.product_id[0].display_name,
            "Plastic Component (Cyan)",
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
        # Add some materials to consume before marking this MO as to do.
        self.mo_sword.action_confirm()

    def test_manufacturing_order_3(self):
        # Delete attribute from sword
        self.product_sword.attribute_line_ids = [(5, 0, 0)]
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.product_sword.product_variant_ids[0]
        # Component skipped
        mo_form.bom_id = self.bom_id
        mo_form.product_qty = 1
        with self.assertRaises(ValidationError):
            # Some attributes of the dynamic component are not included into ...
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
        with self.assertRaises(UserError):
            test_bom_3.explode(self.product_9, 1)
