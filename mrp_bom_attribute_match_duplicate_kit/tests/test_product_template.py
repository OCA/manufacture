# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from .common import TestProductTemplateKitCommon


class TestProductTemplate(TestProductTemplateKitCommon):
    def test_action_duplicate_attribute_match_kit_invalid(self):
        """
        Test flow that catch an error when call
        action_duplicate_attribute_match_kit function
        for product without variants
        """
        with self.assertRaises(UserError):
            self.product_template_without_attributes.action_duplicate_with_kit()

    def test_action_duplicate_attribute_match_Kit_valid(self):
        """
        Test flow that returned wizard action, if product
        has attributes
        """
        product = self.product_template_one_attribute
        self.assertEqual(
            product.product_variant_count,
            2,
            "Product attribute variants count must be equal to 2",
        )
        action = product.action_duplicate_with_kit()
        self.assertIsInstance(action, dict, msg="Returned object must be dict")
        self.assertEqual(
            action["res_model"],
            "product.template.kit.wizard",
            "Res model must be equal to 'product.template.kit.wizard'",
        )
        context = action["context"]
        self.assertIsInstance(context, dict, "Context must be dict")
        self.assertEqual(
            context["default_product_tmpl_id"],
            product.id,
            "Default product template id must be equal to ID {}".format(product.id),
        )
        self.assertEqual(
            context["default_new_product_template_name"],
            product.name + " 1",
            "Default New product template name must be equal to '{} 1'".format(
                product.name
            ),
        )
