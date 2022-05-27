from odoo.exceptions import MissingError, ValidationError
from odoo.tests import Form, tagged

from .common import TestNestedBomCase


@tagged("post_install", "-at_install")
class TestMrpNestedBom(TestNestedBomCase):
    def setUp(self):
        super(TestMrpNestedBom, self).setUp()
        ProductTemplate = self.env["product.template"]

        product_template = Form(ProductTemplate)
        product_template.name = "Log"
        with product_template.attribute_line_ids.new() as pta:
            pta.attribute_id = self.product_attribute_custom
            pta.value_ids.add(self.product_attribute_custom_1)
            pta.value_ids.add(self.product_attribute_custom_1)
        self.product_template_log = product_template.save()

        self.mrp_nested_bom_log = self.env["mrp.nested.bom"].create(
            {
                "parent_id": self.product_template_pinocchio_mrp.id,
                "product_tmpl_id": self.product_template_log.id,
                "product_qty": 4,
            }
        )

    def test_onchange_product_tmpl_id(self):
        self.assertEqual(
            len(self.mrp_nested_bom_wood.attribute_ids),
            0,
            msg="Attributes count must be equal 0",
        )
        self.mrp_nested_bom_wood.write(
            {"product_tmpl_id": self.product_template_log.id}
        )
        self.mrp_nested_bom_wood._onchange_product_tmpl_id()
        self.assertEqual(
            len(self.mrp_nested_bom_wood.attribute_ids),
            1,
            msg="Attributes count must be equal 1",
        )

    def test_compute_all_attribute_ids(self):
        self.assertEqual(
            len(self.mrp_nested_bom_log.all_attribute_ids),
            2,
            msg="Count elements must be equal 2",
        )
        self.product_template_pinocchio_mrp.attribute_line_ids.unlink()
        self.assertEqual(
            len(self.mrp_nested_bom_log.all_attribute_ids),
            1,
            msg="Count elements must be equal 1",
        )

    def test_create_product(self):
        MrpNestedBom = self.env["mrp.nested.bom"]
        with self.assertRaises(MissingError):
            MrpNestedBom.create_product(-1)
        parent = self.product_template_pinocchio_mrp
        result_product_template_id = MrpNestedBom.create_product(parent.id)
        correct_name = "Pinocchio #3"
        product_template = self.get_product(result_product_template_id)
        self.assertEqual(
            product_template.name,
            correct_name,
            msg="Product template name must be equal 'Pinocchio #3'",
        )
        result_product_template_id = MrpNestedBom.create_product(parent.id)
        product_template = self.get_product(result_product_template_id)
        self.assertEqual(
            product_template.name,
            correct_name,
            msg="Product template name must be equal 'Pinocchio #1'",
        )

        self.env["mrp.nested.bom"].create(
            {
                "parent_id": parent.id,
                "product_tmpl_id": result_product_template_id,
                "product_qty": 4,
            }
        )

        correct_name = "Pinocchio #4"
        result_product_template_id = MrpNestedBom.create_product(parent.id)
        product_template = self.get_product(result_product_template_id)
        self.assertEqual(
            product_template.name,
            correct_name,
            msg="Product template name must be equal 'Pinocchio #4'",
        )
        self.env["mrp.nested.bom"].create(
            {
                "parent_id": parent.id,
                "product_tmpl_id": result_product_template_id,
                "product_qty": 5,
            }
        )

        correct_name = "Pinocchio #5"
        result_product_template_id = MrpNestedBom.create_product(parent.id)
        product_template = self.get_product(result_product_template_id)
        self.assertEqual(
            product_template.name,
            correct_name,
            msg="Product template name must be equal 'Pinocchio #5'",
        )

    def test_create_invalid(self):
        with self.assertRaises(
            ValidationError,
            msg="Function create must be raises exception ValidationError",
        ):
            self.env["mrp.nested.bom"].create(
                {"parent_id": self.product_template_pinocchio_mrp.id}
            )

    def test_create_valid(self):
        result = self.env["mrp.nested.bom"].create(
            {"parent_id": self.product_template_log.id, "product_qty": 1}
        )
        self.assertEqual(
            result.product_tmpl_id.name,
            "Log #1",
            msg="Product template name must be equal 'Log #1'",
        )

    def test_prepare_parent_attribute_ids(self):
        result = self.mrp_nested_bom_wood._prepare_parent_attribute_ids()
        self.assertEqual(
            result,
            self.product_attribute_size.ids,
            msg="Attribute must be equal 'Size' id",
        )

    def test_find_product_template_attributes(self):
        result = self.mrp_nested_bom_log._find_product_template_attributes([])
        self.assertEqual(len(result), 0, msg="Attributes count must be equal 0")
        result = self.mrp_nested_bom_log._find_product_template_attributes(
            self.product_attribute_size.ids
        )
        self.assertEqual(len(result), 0, msg="Attributes count must be equal 0")
        result = self.mrp_nested_bom_log._find_product_template_attributes(
            [
                self.product_attribute_size.id,
                self.product_attribute_custom.id,
            ]
        )
        self.assertEqual(len(result), 1, msg="Attributes count must be equal 1")
        self.assertEqual(
            result,
            self.product_attribute_custom,
            msg="Result must be equal 'Custom' product attribute",
        )
        result = self.mrp_nested_bom_log._find_product_template_attributes(
            [
                self.product_attribute_custom.id,
            ]
        )
        self.assertEqual(len(result), 1, msg="Attributes count must be equal 1")
        self.assertEqual(
            result,
            self.product_attribute_custom,
            msg="Result must be equal 'Custom' product attribute",
        )

    def test_prepare_product_attribute(self):
        self.mrp_nested_bom_wood.write(
            {"attribute_ids": [(4, self.product_attribute_size.id)]}
        )
        self.assertEqual(
            len(self.product_template_log.attribute_line_ids),
            1,
            msg="Product Template Attributes count must be equal 1",
        )
        self.assertEqual(
            len(self.product_template_wood.attribute_line_ids),
            0,
            msg="Product Template Attributes count must be equal 0",
        )
        mrp_nested_ids = self.env["mrp.nested.bom"].browse(
            [self.mrp_nested_bom_log.id, self.mrp_nested_bom_wood.id]
        )
        mrp_nested_ids._prepare_product_attribute()
        self.assertEqual(
            len(self.product_template_log.attribute_line_ids),
            2,
            msg="Product Template Attributes count must be equal 2",
        )
        self.assertEqual(
            len(self.product_template_wood.attribute_line_ids),
            0,
            msg="Product Template Attributes count must be equal 0",
        )
