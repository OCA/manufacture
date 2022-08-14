from odoo.exceptions import MissingError, ValidationError
from odoo.tests import Form, tagged

from .common import TestNestedBomCase


@tagged("post_install", "-at_install")
class TestMrpNestedBom(TestNestedBomCase):
    def setUp(self):
        super(TestMrpNestedBom, self).setUp()
        MrpBom = self.env["mrp.bom"]
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
                "bom_id": self.mrp_bom_pinocchio_mrp.id,
                "product_tmpl_id": self.product_template_log.id,
                "product_qty": 4,
            }
        )
        self.mrp_bom_log = MrpBom.create(
            {"product_tmpl_id": self.product_template_log.id, "nested_bom": True}
        )

    def test_onchange_product_tmpl_id(self):
        self.assertEqual(
            len(self.mrp_nested_bom_wood.attribute_ids),
            0,
            msg="Attributes count must be equal to zero",
        )
        self.mrp_nested_bom_wood.write(
            {"product_tmpl_id": self.product_template_log.id}
        )
        self.mrp_nested_bom_wood._onchange_product_tmpl_id()
        self.assertEqual(
            len(self.mrp_nested_bom_wood.attribute_ids),
            1,
            msg="Attributes count must be equal to one",
        )

    def test_compute_attribute_aggregated_ids(self):
        self.assertEqual(
            len(self.mrp_nested_bom_log.attribute_aggregated_ids),
            2,
            msg="Count elements must be equal to two",
        )
        self.product_template_pinocchio_mrp.attribute_line_ids.unlink()
        self.assertEqual(
            len(self.mrp_nested_bom_log.attribute_aggregated_ids),
            1,
            msg="Count elements must be equal to one",
        )

    def test_create_product(self):
        MrpNestedBom = self.env["mrp.nested.bom"]
        result = MrpNestedBom.create_product(MrpNestedBom)
        self.assertFalse(result, msg="Result must be False")
        bom = self.mrp_bom_pinocchio_mrp
        result_product_template_id = MrpNestedBom.create_product(bom)
        correct_name = "Pinocchio #5"
        product_template = self.get_product(result_product_template_id)
        self.assertEqual(
            product_template.name,
            correct_name,
            msg="Product template name must be equal to 'Pinocchio #5'",
        )
        result_product_template_id = MrpNestedBom.create_product(bom)
        product_template = self.get_product(result_product_template_id)
        self.assertEqual(
            product_template.name,
            correct_name,
            msg="Product template name must be equal to 'Pinocchio #1'",
        )

        self.env["mrp.nested.bom"].create(
            {
                "bom_id": bom.id,
                "product_tmpl_id": result_product_template_id,
                "product_qty": 4,
            }
        )

        correct_name = "Pinocchio #6"
        result_product_template_id = MrpNestedBom.create_product(bom)
        product_template = self.get_product(result_product_template_id)
        self.assertEqual(
            product_template.name,
            correct_name,
            msg="Product template name must be equal to 'Pinocchio #6'",
        )
        self.env["mrp.nested.bom"].create(
            {
                "bom_id": bom.id,
                "product_tmpl_id": result_product_template_id,
                "product_qty": 5,
            }
        )

        correct_name = "Pinocchio #7"
        result_product_template_id = MrpNestedBom.create_product(bom)
        product_template = self.get_product(result_product_template_id)
        self.assertEqual(
            product_template.name,
            correct_name,
            msg="Product template name must be equal to 'Pinocchio #7'",
        )

    def test_create_invalid(self):
        with self.assertRaises(
            ValidationError,
            msg="Function create must be raises exception ValidationError",
        ):
            self.env["mrp.nested.bom"].create({"bom_id": self.mrp_bom_log.id})
        with self.assertRaises(MissingError):
            self.env["mrp.nested.bom"].create({})

    def test_create_valid(self):
        result = self.env["mrp.nested.bom"].create(
            {"bom_id": self.mrp_bom_log.id, "product_qty": 1}
        )
        self.assertEqual(
            result.product_tmpl_id.name,
            "Log #1",
            msg="Product template name must be equal to 'Log #1'",
        )

    def test_prepare_bom_product_tmpl_attribute_ids(self):
        result = self.mrp_nested_bom_wood._prepare_bom_product_tmpl_attribute_ids()
        self.assertEqual(result, set(), msg="Result must be empty set")
        self.mrp_nested_bom_wood.attribute_ids = [(4, self.product_attribute_size.id)]
        result = self.mrp_nested_bom_wood._prepare_bom_product_tmpl_attribute_ids()
        self.assertEqual(
            result,
            set(self.product_attribute_size.ids),
            msg="Result must be equal to attribute 'Size' {id}",
        )

    def test_find_product_template_attributes(self):
        result = self.mrp_nested_bom_log._find_product_template_attributes([])
        self.assertEqual(len(result), 0, msg="Attributes count must be equal to zero")
        result = self.mrp_nested_bom_log._find_product_template_attributes(
            self.product_attribute_size.ids
        )
        self.assertEqual(len(result), 0, msg="Attributes count must be equal to zero")
        result = self.mrp_nested_bom_log._find_product_template_attributes(
            [
                self.product_attribute_size.id,
                self.product_attribute_custom.id,
            ]
        )
        self.assertEqual(len(result), 1, msg="Attributes count must be equal to one")
        self.assertEqual(
            result,
            self.product_attribute_custom,
            msg="Result must be equal to 'Custom' product attribute",
        )
        result = self.mrp_nested_bom_log._find_product_template_attributes(
            [
                self.product_attribute_custom.id,
            ]
        )
        self.assertEqual(len(result), 1, msg="Attributes count must be equal to one")
        self.assertEqual(
            result,
            self.product_attribute_custom,
            msg="Result must be equal to 'Custom' product attribute",
        )

    def test_prepare_product_attribute(self):
        self.mrp_nested_bom_wood.write(
            {"attribute_ids": [(4, self.product_attribute_size.id)]}
        )
        self.assertEqual(
            len(self.product_template_log.attribute_line_ids),
            1,
            msg="Product Template Attributes count must be equal to one",
        )
        self.assertEqual(
            len(self.product_template_wood.attribute_line_ids),
            0,
            msg="Product Template Attributes count must be equal to zero",
        )
        mrp_nested_ids = self.env["mrp.nested.bom"].browse(
            [self.mrp_nested_bom_log.id, self.mrp_nested_bom_wood.id]
        )
        mrp_nested_ids._prepare_product_attribute()
        self.assertEqual(
            len(self.product_template_log.attribute_line_ids),
            1,
            msg="Product Template Attributes count must be equal to one",
        )
        self.assertEqual(
            len(self.product_template_wood.attribute_line_ids),
            1,
            msg="Product Template Attributes count must be equal to one",
        )
