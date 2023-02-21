from datetime import datetime, timedelta

from odoo.tests import common


class TestAnalytic(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.analytic_job1 = self.browse_ref("mrp_account_analytic_wip.analytic_job1")
        self.final_machine = self.browse_ref("mrp_account_analytic_wip.final_machine")
        self.bom_final_machine = self.browse_ref(
            "mrp_account_analytic_wip.bom_final_machine"
        )
        self.uom_unit = self.browse_ref("uom.product_uom_unit")
        self.mrp_workcenter = self.browse_ref("mrp_account_analytic_wip.mrp_workcenter")
        self.productive_time = self.browse_ref("mrp.block_reason7")
        # Create MO
        mo_job1_obj = self.env["mrp.production"]
        vals = {
            "product_id": self.final_machine.id,
            "bom_id": self.bom_final_machine.id,
            "product_qty": 1,
            "analytic_account_id": self.analytic_job1.id,
        }
        self.mo_job1 = mo_job1_obj.create(vals)

    def test_100_start_job_mo(self):
        # Click on CONFIRM button, generates Tracking Items
        self.assertEqual(self.mo_job1.analytic_tracking_item_count, 0)
        self.mo_job1.action_confirm()
        self.assertEqual(self.mo_job1.analytic_tracking_item_count, 8)

        # == Workorders ==
        # Start time on Operation 1, generates WIP
        # Hourly cost=100, planned time = 30m = 0.5h -> 50$
        # Actual time = 0.25h * $100/h = $25
        workorder1 = self.mo_job1.workorder_ids[0]
        time0 = datetime.now()
        time1 = time0 + timedelta(minutes=15)
        workorder1.time_ids.create(
            {
                "workorder_id": workorder1.id,
                "workcenter_id": self.mrp_workcenter.id,
                "loss_id": self.productive_time.id,
                "date_start": time0,
                "date_end": time1,
                "duration": 2.00,
                "production_id": self.mo_job1.id,
            }
        )
        tracking1 = self.mo_job1.analytic_tracking_item_ids.filtered(
            lambda x: x.workorder_id == workorder1
        )
        actual_amount = sum(tracking1.mapped("actual_amount"))
        self.assertEqual(actual_amount, 25.0)
        # Start time on Operation 2, generates WIP and Variance
        # Hourly cost=100, planned time = 30m = 0.5h -> $50
        # Actual time = 0.75h * $100/h = $75
        workorder2 = self.mo_job1.workorder_ids[1]
        time0, time1 = time1, time1 + timedelta(minutes=45)
        workorder2.time_ids.create(
            {
                "workorder_id": workorder2.id,
                "workcenter_id": self.mrp_workcenter.id,
                "loss_id": self.productive_time.id,
                "date_start": time0,
                "date_end": time1,
                "duration": 2.00,
            }
        )
        tracking2 = self.mo_job1.analytic_tracking_item_ids.filtered(
            lambda x: x.workorder_id == workorder2
        )
        actual_amount = sum(tracking2.mapped("actual_amount"))
        self.assertEqual(actual_amount, 75.0)
        wip_amount = sum(tracking2.mapped("wip_actual_amount"))
        self.assertEqual(wip_amount, 0.0)
        var_amount = sum(tracking2.mapped("variance_actual_amount"))
        self.assertEqual(var_amount, 75.0)

        # TODO: Raw Materials WIP and Variance
        # TODO: daily Post to accounting
        # TODO: MO Done

    def test_200_edit_mo_analytic(self):
        mo = self.mo_job1
        analytic_plan = self.env["account.analytic.plan"].create(
            {"name": "Plan Test", "company_id": False}
        )
        aa_job2 = self.env["account.analytic.account"].create(
            {"name": "New Analytic Account", "plan_id": analytic_plan.id}
        )
        mo.analytic_account_id = aa_job2
        self.assertEqual(mo.analytic_account_id, aa_job2)
        self.mo_job1.action_confirm()
        # No exception expected
