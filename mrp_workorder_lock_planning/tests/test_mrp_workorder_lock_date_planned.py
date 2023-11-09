# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.exceptions import ValidationError
from odoo.tests import Form, TransactionCase


class TestMrpWorkorderLockDatePlanned(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bom_with_routing = cls.env.ref("mrp.mrp_bom_drawer_rout")
        cls.product_with_routing = (
            cls.bom_with_routing.product_tmpl_id.product_variant_id
        )

    @classmethod
    def _create_manufacturing_order(cls, qty=1.0):
        mo_form = Form(cls.env["mrp.production"])
        mo_form.product_id = cls.product_with_routing
        mo_form.bom_id = cls.bom_with_routing
        mo_form.product_qty = qty
        return mo_form.save()

    def test_lock_planning_cannot_lock(self):
        mo = self._create_manufacturing_order()
        mo.action_confirm()
        with self.assertRaisesRegex(ValidationError, "Cannot lock planning"):
            mo.workorder_ids[0].toggle_lock_planning()

    def test_lock_planning_is_locked(self):
        mo = self._create_manufacturing_order()
        mo.action_confirm()
        mo.button_plan()
        mo.workorder_ids[0].toggle_lock_planning()
        self.assertTrue(mo.workorder_ids[0].lock_planning)
        with self.assertRaisesRegex(ValidationError, "Workorder is locked"):
            mo.button_unplan()
