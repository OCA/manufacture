# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import new_test_user

from odoo.addons.mrp.tests.common import TestMrpCommon


@tagged("post_install", "-at_install")
class TestStockMrpTierValidation(TestMrpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.py_model = cls.env.ref("mrp.model_mrp_production")
        cls.test_user = new_test_user(
            cls.env,
            name="Test User",
            login="test_user",
            groups="base.group_system,mrp.group_mrp_user",
        )
        cls.tier_def_obj = cls.env["tier.definition"]
        cls.tier_def_obj.create(
            {
                "model_id": cls.py_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user.id,
                "definition_domain": "[('origin', '=', False)]",
            }
        )

    def test_tier_validation_production(self):
        """
        If the manufacturing order does not have the origin field filled in,
        it cannot be validated
        """
        mo, bom_id, _p_final, _p1, _p2 = self.generate_mo()
        # The origin field is empty, so the validation should
        # be triggered when trying to mark as done
        mo.origin = False
        mo.invalidate_model()
        msg_error_mark_done = (
            "This action needs to be validated for at least "
            "one record. \nPlease request a validation."
        )
        with self.assertRaisesRegex(ValidationError, msg_error_mark_done):
            mo.button_mark_done()
        mo.request_validation()
        mo.invalidate_model()
        msg_error_open = (
            r"(?s)A validation process is still open for at least one record\."
        )
        with self.assertRaisesRegex(ValidationError, msg_error_open):
            mo.button_mark_done()
        mo = mo.with_user(self.test_user)
        mo.validate_tier()
        mo.invalidate_model()
        mo.button_mark_done()
        self.assertEqual(mo.state, "done")
        mo1, bom_id, _p_final, _p1, _p2 = self.generate_mo()
        mo1.origin = "test"
        mo1.button_mark_done()
        self.assertEqual(mo1.state, "done")

    def test_tier_validation_exception(self):
        """
        If a manufacturing order not has a exception,
        when requesting validation, the user will be able to write
        any field.
        """
        mo, bom_id, _p_final, _p1, _p2 = self.generate_mo()
        mo.invalidate_model()
        mo.origin = False
        mo.request_validation()
        write_error = "You are not allowed to write those fields under validation."
        with self.assertRaisesRegex(ValidationError, write_error):
            mo.write({"origin": "test"})
