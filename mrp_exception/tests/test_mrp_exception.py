from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestMrpException(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
            }
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_qty": 1.0,
            }
        )
        cls.rule = cls.env["exception.rule"].create(
            {
                "name": "Block MO > 100 Qty",
                "model": "mrp.production",
                "exception_type": "by_domain",
                "domain": "[('product_qty', '>', 100)]",
                "active": True,
            }
        )

    def _create_mo(self, qty):
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": qty,
                "bom_id": self.bom.id,
            }
        )
        mo.action_confirm()
        return mo

    def test_mo_no_exception(self):
        """MO without exception completes successfully."""
        mo = self._create_mo(10.0)
        mo.button_mark_done()
        self.assertEqual(mo.state, "done")

    def test_mo_with_exception_blocks_and_maps_relations(self):
        """MO with exception pops wizard and sets up Many2many mappings."""
        mo = self._create_mo(150.0)

        action = mo.button_mark_done()

        self.assertEqual(mo.state, "confirmed")
        self.assertEqual(action["res_model"], "mrp.exception.confirm")
        self.assertEqual(action["target"], "new")
        self.assertEqual(action["context"]["active_model"], "mrp.production")
        self.assertEqual(action["context"]["active_ids"], mo.ids)

        # Verify the OCA engine correctly mapped the reverse relationships
        self.assertIn(self.rule, mo.exception_ids)
        self.assertIn(mo, self.rule.production_ids)

    def test_mo_exception_ignored_via_wizard(self):
        """Ignoring an exception through the wizard resumes the MO workflow."""
        mo = self._create_mo(150.0)
        action = mo.button_mark_done()

        wizard = (
            self.env["mrp.exception.confirm"]
            .with_context(**action["context"])
            .create(
                {
                    "ignore": True,
                    "related_model_id": mo.id,
                }
            )
        )

        wizard.action_confirm()

        self.assertEqual(mo.state, "done")
        self.assertTrue(mo.ignore_exception)

    def test_blocking_exception_cannot_be_ignored(self):
        """A blocking exception should raise a UserError when a bypass is attempted."""
        self.rule.write({"is_blocking": True})
        mo = self._create_mo(150.0)
        action = mo.button_mark_done()

        wizard = (
            self.env["mrp.exception.confirm"]
            .with_context(**action["context"])
            .create(
                {
                    "ignore": True,
                    "related_model_id": mo.id,
                }
            )
        )

        with self.assertRaises(UserError):
            wizard.action_confirm()
