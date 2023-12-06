# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, SavepointCase


class TestProductTemplateKitCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProductTemplateKitCommon, cls).setUpClass()
        # Attribute Color
        cls.attribute_color = cls.env.ref("product.product_attribute_2")

        # Attribute Color Values
        cls.attribute_color_white = cls.env.ref("product.product_attribute_value_3")
        cls.attribute_color_black = cls.env.ref("product.product_attribute_value_4")

        # Attribute Legs
        cls.attribute_legs = cls.env.ref("product.product_attribute_1")

        # Attribute Legs Values
        cls.attribute_legs_steel = cls.env.ref("product.product_attribute_value_1")
        cls.attribute_legs_aluminium = cls.env.ref("product.product_attribute_value_2")

        # Product Without Attributes
        cls.product_template_without_attributes = cls.env["product.template"].create(
            {"name": "Product Without Attributes"}
        )

        # Product With One Attribute
        form = Form(cls.env["product.template"])
        form.name = "Product With One Attribute"
        with form.attribute_line_ids.new() as line:
            line.attribute_id = cls.attribute_color
            line.value_ids.add(cls.attribute_color_white)
            line.value_ids.add(cls.attribute_color_black)
        cls.product_template_one_attribute = form.save()

        # Product With Many Attributes
        form = Form(cls.env["product.template"])
        form.name = "Product With One Attribute"
        with form.attribute_line_ids.new() as line:
            line.attribute_id = cls.attribute_color
            line.value_ids.add(cls.attribute_color_white)
            line.value_ids.add(cls.attribute_color_black)
        with form.attribute_line_ids.new() as line:
            line.attribute_id = cls.attribute_legs
            line.value_ids.add(cls.attribute_legs_steel)
            line.value_ids.add(cls.attribute_legs_aluminium)
        cls.product_template_two_attributes = form.save()
