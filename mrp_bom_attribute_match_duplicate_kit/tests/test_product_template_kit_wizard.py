# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import Form

from .common import TestProductTemplateKitCommon


class TestProductTemplateKitWizard(TestProductTemplateKitCommon):
    def test_action_confirm_invalid(self):
        """
        Test flow that catch error when product template name
        and new product template name is the same
        """
        context = {
            "default_product_tmpl_id": self.product_template_one_attribute.id,
        }
        form = Form(self.env["product.template.kit.wizard"].with_context(**context))
        form.new_product_template_name = self.product_template_one_attribute.name
        wizard = form.save()

        with self.assertRaises(UserError):
            wizard.action_confirm()

    def test_action_confirm_flow(self):
        """Test flow that run full workflow"""
        product = self.product_template_two_attributes
        context = {
            "default_product_tmpl_id": product.id,
            "default_new_product_template_name": "{} 1".format(product.name),
        }

        wizard = Form(
            self.env["product.template.kit.wizard"].with_context(**context)
        ).save()
        action = wizard.action_confirm()

        self.assertIsInstance(action, dict, "Action must be dict")

        new_product_name = "{} 1".format(product.name)
        self.assertEqual(
            action["name"],
            new_product_name,
            "Action name must be equal to {}".format(new_product_name),
        )
        self.assertTrue(action.get("res_id"), "Res ID key must be exists")

        product_tmpl = self.env["product.template"].browse(action["res_id"])

        self.assertEqual(product_tmpl.name, new_product_name, "Names must be the same")

        boms = product_tmpl.bom_ids
        self.assertTrue(boms, "BOM's must be exists")
        self.assertEqual(len(boms), 1, "Count BOM's must be equal to 1")
        self.assertEqual(
            boms.product_tmpl_id.id,
            product_tmpl.id,
            "BOMs product and new product must be the same",
        )
        self.assertEqual(boms.type, "phantom")
        self.assertEqual(boms.product_qty, 1, "Product Qty must be equal to 1")
        self.assertTrue(boms.bom_line_ids, "BOM must have Lines")
        self.assertEqual(len(boms.bom_line_ids), 1, msg="BOM must have one line")

        line = boms.bom_line_ids
        self.assertEqual(
            line.component_template_id.id,
            product.id,
            "Component product template ID must be equal to ID {}".format(product.id),
        )
        self.assertListEqual(
            line.match_on_attribute_ids.ids,
            [self.attribute_legs.id, self.attribute_color.id],
            "Attributes must be the same",
        )
        self.assertEqual(line.product_qty, 1, "Product Qty must be equal to 1")
