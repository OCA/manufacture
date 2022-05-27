from odoo.tests import Form, common


class TestNestedBomCase(common.TransactionCase):
    def setUp(self):
        super(TestNestedBomCase, self).setUp()
        ProductAttribute = self.env["product.attribute"]
        ProductAttributeValue = self.env["product.attribute.value"]
        ProductTemplate = self.env["product.template"]

        self.product_attribute_size = ProductAttribute.create(
            {
                "name": "Size",
            }
        )

        self.product_attribute_custom = ProductAttribute.create({"name": "Custom"})

        self.product_attribute_size_medium = ProductAttributeValue.create(
            {
                "name": "Medium",
                "attribute_id": self.product_attribute_size.id,
            }
        )
        self.product_attribute_size_large = ProductAttributeValue.create(
            {
                "name": "Large",
                "attribute_id": self.product_attribute_size.id,
            }
        )
        self.product_attribute_custom_1 = ProductAttributeValue.create(
            {
                "name": "Custom #1",
                "attribute_id": self.product_attribute_custom.id,
            }
        )
        self.product_attribute_custom_2 = ProductAttributeValue.create(
            {
                "name": "Custom #2",
                "attribute_id": self.product_attribute_custom.id,
            }
        )

        self.product_template_wood = ProductTemplate.create(
            {
                "name": "Wood",
            }
        )

        product_template = Form(self.env["product.template"])
        product_template.name = "Pinocchio"
        with product_template.attribute_line_ids.new() as pta:
            pta.attribute_id = self.product_attribute_size
            pta.value_ids.add(self.product_attribute_size_medium)
            pta.value_ids.add(self.product_attribute_size_large)
        with product_template.nested_bom_ids.new() as nested:
            nested.product_qty = 3
            nested.attribute_ids.add(self.product_attribute_size)
        with product_template.nested_bom_ids.new() as nested:
            nested.product_qty = 2
            nested.attribute_ids.add(self.product_attribute_size)

        with product_template.nested_bom_ids.new() as nested:
            nested.product_tmpl_id = self.product_template_wood
            nested.product_qty = 1
        self.product_template_pinocchio = product_template.save()

        product_template_mrp = Form(self.env["product.template"])
        product_template_mrp.name = "Pinocchio"
        with product_template_mrp.attribute_line_ids.new() as pta:
            pta.attribute_id = self.product_attribute_size
            pta.value_ids.add(self.product_attribute_size_medium)
            pta.value_ids.add(self.product_attribute_size_large)
        self.product_template_pinocchio_mrp = product_template_mrp.save()

        self.mrp_nested_bom_wood = self.env["mrp.nested.bom"].create(
            {
                "parent_id": self.product_template_pinocchio_mrp.id,
                "product_tmpl_id": self.product_template_wood.id,
                "product_qty": 3,
            }
        )

    def get_product(self, id_):
        return self.env["product.template"].browse(id_)
