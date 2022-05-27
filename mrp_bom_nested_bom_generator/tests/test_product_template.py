from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import TestNestedBomCase


@tagged("post_install", "-at_install")
class TestProductTemplate(TestNestedBomCase):
    def test_nested_bom_count(self):
        nested_count = self.product_template_pinocchio.nested_bom_count
        self.assertEqual(nested_count, 3, msg="Nested BOM Count must be equal 3")

    def test_prepare_temp_nested_bom_item(self):
        temp_nested_bom = (
            self.product_template_pinocchio._prepare_temp_nested_bom_item()
        )
        self.assertEqual(
            temp_nested_bom._name,
            "mrp.nested.bom",
            msg="Model name must be equal 'mrp.nested.bom'",
        )
        self.assertEqual(temp_nested_bom.ids, [], msg="Ids field must be empty list")
        self.assertNotEqual(
            type(temp_nested_bom.id), int, msg="Id field type must be not equal int"
        )
        self.assertEqual(
            temp_nested_bom.parent_id,
            self.product_template_pinocchio,
            msg="Parent product must be equal 'Pinocchio' product template",
        )
        self.assertEqual(
            temp_nested_bom.product_tmpl_id,
            self.product_template_pinocchio,
            msg="Product template must be equal 'Pinocchio' product template",
        )
        self.assertEqual(
            temp_nested_bom.product_qty, 1, msg="Product Qty must be equal 1"
        )
        self.assertEqual(
            temp_nested_bom.uom_id,
            self.product_template_pinocchio.uom_id,
            msg="Uom must br equal 'Pinocchio' product uom",
        )

    def test_group_by_stage(self):
        p0, p1, p2 = list(self.product_template_pinocchio.nested_bom_ids)
        stages = list(self.product_template_pinocchio.group_by_stage())
        self.assertEqual(len(stages), 3, msg="Stages count must be equal 3")
        f_stage, s_stage, t_stage = stages
        self.assertEqual(
            f_stage[0].product_tmpl_id,
            self.product_template_pinocchio,
            msg="First stage product template must be equal 'Pinocchio' product template",
        )
        self.assertEqual(f_stage[1], p0)
        self.assertEqual(s_stage, (p0, p1))
        self.assertEqual(t_stage, (p1, p2))

    def test_action_generate_nested_boms_invalid(self):
        self.product_template_pinocchio.nested_bom_ids.unlink()
        with self.assertRaises(
            UserError, msg="Function must be raises exception UserError"
        ):
            self.product_template_pinocchio.action_generate_nested_boms()

    def test_action_generate_nested_boms_valid(self):
        result = self.product_template_pinocchio.action_generate_nested_boms()
        self.assertIsNone(result, msg="Function must be return None")

    def test_create_boms_valid(self):
        MrpBom = self.env["mrp.bom"]
        product_tmpl_ids = self.product_template_pinocchio.nested_bom_ids.mapped(
            "product_tmpl_id"
        )
        product_tmpl_ids |= self.product_template_pinocchio
        self.product_template_pinocchio.create_boms()
        mrp_bom_ids = MrpBom.search([("product_tmpl_id", "in", product_tmpl_ids.ids)])
        self.assertEqual(len(mrp_bom_ids), 3, msg="MRP BOM count must be equal 3")

    def test_create_boms_invalid(self):
        MrpBom = self.env["mrp.bom"]
        product_tmpl_ids = self.product_template_pinocchio.nested_bom_ids.mapped(
            "product_tmpl_id"
        )
        product_tmpl_ids |= self.product_template_pinocchio

        self.product_template_pinocchio.nested_bom_ids.unlink()

        self.product_template_pinocchio.create_boms()
        mrp_bom_ids = MrpBom.search([("product_tmpl_id", "in", product_tmpl_ids.ids)])
        self.assertEqual(len(mrp_bom_ids), 0, msg="MRP BOM count must be equal 0")
