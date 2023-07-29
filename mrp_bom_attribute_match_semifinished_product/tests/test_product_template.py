from odoo.exceptions import UserError
from odoo.tests import Form

from .test_finished_product_common import TestFinishedProductCommon


class TestProductTemplate(TestFinishedProductCommon):
    def test_create_product_template_without_attributes(self):
        """Test flow when finished product created without attributes"""
        form = Form(self.env["product.template"])
        form.name = "Product #2"
        form.finished_product = True
        with self.assertRaises(UserError):
            form.save()

    def test_edit_attributes_in_finished_product_template(self):
        """Test flow when all attribute is removed from finished product"""
        with self.assertRaises(UserError), Form(self.product_1) as form:
            form.attribute_line_ids.remove(index=1)
            form.attribute_line_ids.remove(index=0)

    def test_action_finished_product_structure_invalid(self):
        """Test flow when action is raised error for not finished product"""
        self.product_1.finished_product = False
        with self.assertRaises(UserError):
            self.product_1.action_finished_product_structure()

    def test_action_finished_product_structure_valid(self):
        """Test flow when action is correct for finished product"""
        action = self.product_1.action_finished_product_structure()
        self.assertEqual(
            action.get("type"),
            "ir.actions.act_window",
            msg="Action type must be equal to 'ir.actions.act_window'",
        )
        self.assertEqual(
            action.get("view_mode"),
            "form",
            msg="Action view mode must be equal to 'form'",
        )
        self.assertEqual(
            action.get("res_model"),
            "finished.product.structure.wizard",
            msg="Action res model must be equal to 'finished.product.structure.wizard'",
        )
        self.assertEqual(
            action.get("target"), "new", msg="Action target must be equal to 'new'"
        )
        context = {"default_finished_product_id": self.product_1.id}
        self.assertDictEqual(
            action.get("context"), context, msg="Contexts must be the same"
        )
