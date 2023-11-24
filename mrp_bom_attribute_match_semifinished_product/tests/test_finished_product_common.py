from odoo.tests import Form, TransactionCase


class TestFinishedProductCommon(TransactionCase):
    def setUp(self):
        super(TestFinishedProductCommon, self).setUp()

        # Legs Attribute
        self.legs_attribute = self.env.ref("product.product_attribute_1")
        self.legs_steel_attr_value = self.env.ref("product.product_attribute_value_1")
        self.legs_aluminium_attr_value = self.env.ref(
            "product.product_attribute_value_2"
        )

        # Color Attribute
        self.color_attribute = self.env.ref("product.product_attribute_2")
        self.color_white_attr_value = self.env.ref("product.product_attribute_value_3")
        self.color_black_attr_value = self.env.ref("product.product_attribute_value_4")

        # Create Valid Product
        form = Form(self.env["product.template"])
        form.name = "Product #1"
        form.finished_product = True
        with form.attribute_line_ids.new() as attribute:
            attribute.attribute_id = self.legs_attribute
            attribute.value_ids.add(self.legs_steel_attr_value)
            attribute.value_ids.add(self.legs_aluminium_attr_value)
        with form.attribute_line_ids.new() as attribute:
            attribute.attribute_id = self.color_attribute
            attribute.value_ids.add(self.color_white_attr_value)
            attribute.value_ids.add(self.color_black_attr_value)
        self.product_1 = form.save()
