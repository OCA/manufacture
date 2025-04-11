# Copyright 2025 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestMrpWorkorderLastWorker(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.config.settings"].create({"group_mrp_routings": True}).execute()
        cls.bom_rout = cls.env.ref("mrp.mrp_bom_drawer_rout")
        cls.product_rout = cls.bom_rout.product_tmpl_id.product_variant_id
        cls.user_1 = cls.env.ref("base.user_admin")
        cls.user_2 = cls.env.ref("base.user_demo")

    @classmethod
    def _create_manufacturing_order(cls, qty=1.0):
        mo_form = Form(cls.env["mrp.production"])
        mo_form.product_id = cls.product_rout
        mo_form.bom_id = cls.bom_rout
        mo_form.product_qty = qty
        return mo_form.save()

    @classmethod
    def _create_workcenter_productivity(
        cls, workorder, user, date_start, date_end=False
    ):
        return cls.env["mrp.workcenter.productivity"].create(
            {
                "workorder_id": workorder.id,
                "workcenter_id": workorder.workcenter_id.id,
                "user_id": user.id,
                "date_start": date_start,
                "date_end": date_end,
                "loss_id": cls.env.ref("mrp.block_reason7").id,
            }
        )

    def test_workorder_last_worker(self):
        # Create a manufacturing order with 3 workorders
        mo = self._create_manufacturing_order()
        mo.action_confirm()
        mo.button_plan()
        self.assertEqual(len(mo.workorder_ids), 3)
        workorder_1 = mo.workorder_ids[0]
        # Since the workorder is not started yet, the last worker should be False
        self.assertFalse(workorder_1.last_worker_id)
        # Create a workcenter productivity for user_1
        # The last worker should be user_1 then, either with or without date_end
        workcenter_productivity_1 = self._create_workcenter_productivity(
            workorder_1, self.user_1, "2025-01-01 10:00:00"
        )
        self.assertEqual(workorder_1.last_worker_id, self.user_1)
        workcenter_productivity_1.write({"date_end": "2025-01-01 11:00:00"})
        self.assertEqual(workorder_1.last_worker_id, self.user_1)
        # Create a workcenter productivity for user_2
        # The last worker should be user_2 then, either with or without date_end
        # because the date_end of user_1 is before the date_start of user_2
        workcenter_productivity_2 = self._create_workcenter_productivity(
            workorder_1, self.user_2, "2025-01-01 12:00:00"
        )
        self.assertEqual(workorder_1.last_worker_id, self.user_2)
        workcenter_productivity_2.write({"date_end": "2025-01-01 13:00:00"})
        self.assertEqual(workorder_1.last_worker_id, self.user_2)
        # Change the dates if workcenter productivity 1 to be after workcenter
        # productivity 2, the last worker should be user_1 then
        workcenter_productivity_1.write(
            {"date_start": "2025-01-01 14:00:00", "date_end": "2025-01-01 15:00:00"}
        )
        self.assertEqual(workorder_1.last_worker_id, self.user_1)
