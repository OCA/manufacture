# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMrpProductionCancelConfirm(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Models
        cls.MrpProduction = cls.env["mrp.production"]
        # Instances
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "is_storable": True}
        )
        cls.production = cls._create_production()

    @classmethod
    def _create_production(cls, **kwargs):
        vals = {
            "product_id": cls.product.id,
            "product_qty": 1.0,
            "product_uom_id": cls.product.uom_id.id,
        }
        vals.update(kwargs)
        return cls.MrpProduction.create(vals)

    def _cancel_from_button(self, production):
        """Cancel as the Cancel button of the views does"""
        return production.with_context(cancel_confirm_wizard=True).action_cancel()

    def test_01_cancel_confirm_production(self):
        """Cancel a document from the button, I expect cancel_reason"""
        self.production.action_confirm()
        # Click cancel, cancel confirm wizard will open. Type in cancel_reason
        res = self._cancel_from_button(self.production)
        ctx = res.get("context")
        self.assertEqual(ctx["cancel_method"], "action_cancel")
        self.assertEqual(ctx["default_has_cancel_reason"], "optional")
        self.assertEqual(self.production.state, "confirmed")
        wizard = Form(self.env["cancel.confirm"].with_context(**ctx))
        wizard.cancel_reason = "Wrong information"
        wiz = wizard.save()
        # Confirm cancel on wizard
        wiz.confirm_cancel()
        self.assertEqual(self.production.cancel_reason, "Wrong information")
        self.assertEqual(self.production.cancel_by, self.env.user)
        self.assertTrue(self.production.cancel_date)
        self.assertEqual(self.production.state, "cancel")

    def test_02_cancel_not_from_button(self):
        """Cancellations not coming from the Cancel button are not confirmed,
        so that flows cancelling manufacturing orders on their own still work.
        """
        self.production.action_confirm()
        self.production.action_cancel()
        self.assertEqual(self.production.state, "cancel")
        self.assertFalse(self.production.cancel_reason)

    def test_03_unlink_production(self):
        """Deleting a manufacturing order cancels it first, without wizard"""
        production = self._create_production()
        production.unlink()
        self.assertFalse(production.exists())
