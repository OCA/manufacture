from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import TestNestedBomCase


@tagged("post_install", "-at_install")
class TestMrpBom(TestNestedBomCase):
    def test_prepare_temp_nested_bom_item(self):
        temp_nested_bom = self.mrp_bom_pinocchio._prepare_temp_nested_bom_item()
        self.assertEqual(
            temp_nested_bom._name,
            "mrp.nested.bom",
            msg="Model name must be equal to 'mrp.nested.bom'",
        )
        self.assertEqual(temp_nested_bom.ids, [], msg="Ids field must be empty list")
        self.assertNotEqual(
            type(temp_nested_bom.id), int, msg="Id field type must be not int type"
        )
        self.assertEqual(
            temp_nested_bom.bom_product_tmpl_id,
            self.product_template_pinocchio,
            msg="Parent product must be equal to 'Pinocchio' product template",
        )
        self.assertEqual(
            temp_nested_bom.product_tmpl_id,
            self.product_template_pinocchio,
            msg="Product template must be equal to 'Pinocchio' product template",
        )
        self.assertEqual(
            temp_nested_bom.product_qty, 1, msg="Product Qty must be equal to one"
        )
        self.assertEqual(
            temp_nested_bom.uom_id,
            self.product_template_pinocchio.uom_id,
            msg="Uom must br equal to 'Pinocchio' product uom",
        )

    def test_group_by_stage(self):
        p0, p1, p2 = list(self.mrp_bom_pinocchio.nested_bom_ids)
        stages = list(self.mrp_bom_pinocchio.group_by_stage())
        self.assertEqual(len(stages), 3, msg="Stages count must be equal to three")
        f_stage, s_stage, t_stage = stages
        self.assertEqual(
            f_stage[0].product_tmpl_id,
            self.product_template_pinocchio,
            msg="First stage product template must be equal to 'Pinocchio' product template",
        )
        self.assertEqual(f_stage[1], p0)
        self.assertEqual(s_stage, (p0, p1))
        self.assertEqual(t_stage, (p1, p2))

    def test_action_generate_nested_boms_invalid(self):
        result = self.mrp_bom_pinocchio.action_generate_nested_boms()
        self.assertTrue(result, msg="Result must be True")
        self.mrp_bom_pinocchio.nested_bom_ids.unlink()
        with self.assertRaises(
            UserError, msg="Function must be raises exception UserError"
        ):
            self.mrp_bom_pinocchio.action_generate_nested_boms()

    def test_action_generate_nested_boms_valid(self):
        result = self.mrp_bom_pinocchio_mrp.action_generate_nested_boms()
        self.assertTrue(result, msg="Function result must be True")
        self.assertEqual(
            len(self.product_template_wood.bom_ids),
            2,
            msg="Duplicates count mrp for product template must be equal to two",
        )
        result = self.mrp_bom_pinocchio_mrp.action_generate_nested_boms()
        self.assertTrue(result, msg="Function result must be True")

    def test_create_boms_valid(self):
        MrpBom = self.env["mrp.bom"]
        product_tmpl_ids = self.mrp_bom_pinocchio.nested_bom_ids.mapped(
            "product_tmpl_id"
        )
        product_tmpl_ids |= self.product_template_pinocchio
        self.mrp_bom_pinocchio.create_boms()
        mrp_bom_ids = MrpBom.search([("product_tmpl_id", "in", product_tmpl_ids.ids)])
        self.assertEqual(
            len(mrp_bom_ids), 3, msg="MRP BOM count must be equal to three"
        )

    def test_create_boms_invalid(self):
        product_tmpl_ids = self.mrp_bom_pinocchio.nested_bom_ids.mapped(
            "product_tmpl_id"
        )
        product_tmpl_ids |= self.product_template_pinocchio

        self.mrp_bom_pinocchio.nested_bom_ids.unlink()

        self.mrp_bom_pinocchio.create_boms()
        child_bom_ids = self.mrp_bom_pinocchio.child_bom_ids
        self.assertEqual(
            len(child_bom_ids), 0, msg="MRP BOM count must be equal to zero"
        )

    def test_unlink_existing_bom(self):
        status = self.mrp_bom_pinocchio.unlink_existing_bom()
        self.assertFalse(status, msg="Function result must be False")
        self.mrp_bom_pinocchio.action_generate_nested_boms()
        status = self.mrp_bom_pinocchio.unlink_existing_bom()
        self.assertTrue(status, msg="Function result must be True")

    def test_action_open_parent_bom(self):
        self.mrp_bom_pinocchio.action_generate_nested_boms()
        mrp_bom_ids = self.mrp_bom_pinocchio | self.mrp_bom_pinocchio_mrp
        with self.assertRaises(ValueError):
            mrp_bom_ids.action_open_parent_bom()
        first_child_bom = self.mrp_bom_pinocchio.child_bom_ids[0]
        action_dict = first_child_bom.action_open_parent_bom()
        res_id = action_dict.get("res_id", False)
        self.assertEqual(
            self.mrp_bom_pinocchio.id,
            res_id,
            msg="Res id must be equal to {}".format(self.mrp_bom_pinocchio.id),
        )

    def test_create_mrp_bom_record_invalid(self):
        error_msg = "Result must be False"
        valid_lines = [
            (
                0,
                0,
                {
                    "product_id": self.product_template_wood.id,
                    "product_qty": 2.0,
                    "bom_product_template_attribute_value_ids": [],
                },
            )
        ]
        invalid_lines = []
        product = self.mrp_bom_pinocchio.nested_bom_ids[0]
        result = self.mrp_bom_pinocchio._create_mrp_bom_record(
            self.env["mrp.nested.bom"], valid_lines
        )
        self.assertFalse(result, error_msg)
        result = self.mrp_bom_pinocchio._create_mrp_bom_record(product, invalid_lines)
        self.assertFalse(result, error_msg)
        invalid_lines = [(4, "invalid")]
        result = self.mrp_bom_pinocchio._create_mrp_bom_record(product, invalid_lines)
        self.assertFalse(result, error_msg)
        invalid_lines = [
            (
                1,
                0,
                {
                    "product_id": self.product_template_wood.id,
                    "product_qty": 2.0,
                    "bom_product_template_attribute_value_ids": [],
                },
            )
        ]
        result = self.mrp_bom_pinocchio._create_mrp_bom_record(product, invalid_lines)
        self.assertFalse(result, error_msg)
        invalid_lines = [(0, 0, ("invalid", "type"))]
        result = self.mrp_bom_pinocchio._create_mrp_bom_record(product, invalid_lines)
        self.assertFalse(result, error_msg)
