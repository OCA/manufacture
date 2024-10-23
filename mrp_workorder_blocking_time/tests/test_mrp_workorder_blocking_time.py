# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import timedelta

from odoo.tests import Form, TransactionCase, tagged


# use "tagged" based on https://github.com/odoo/odoo/issues/18002
@tagged("post_install", "-at_install")
class TestMrpWorkorderBlockingTime(TransactionCase):
    def create_production_to_test(self):
        # create new production order
        mrp_order_form = Form(self.env["mrp.production"])
        mrp_order_form.product_id = self.product_to_build
        mrp_order_form.product_qty = 1
        production = mrp_order_form.save()

        return production

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_to_build = cls.env["product.product"].create(
            {
                "name": "Young Tom",
                "type": "product",
            }
        )
        cls.product_to_use_1 = cls.env["product.product"].create(
            {
                "name": "Botox",
                "type": "product",
            }
        )
        cls.bom_1 = cls.env["mrp.bom"].create(
            {
                "product_id": cls.product_to_build.id,
                "product_tmpl_id": cls.product_to_build.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "consumption": "flexible",
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.product_to_use_1.id, "product_qty": 1})
                ],
            }
        )

        cls.workcenter_1 = cls.env["mrp.workcenter"].create(
            {
                "name": "Workcenter 1",
            }
        )

        cls.operationWithBlockingTime = cls.env["mrp.routing.workcenter"].create(
            {
                "name": "Operation 1",
                "bom_id": cls.bom_1.id,
                "workcenter_id": cls.workcenter_1.id,
                "time_cycle": 1,
                "time_mode": "manual",
                "time_cycle_manual": 60.0,
                "blocking_stage": True,
                "recommended_blocking_time": 1.5,
                "sequence": 1,
            }
        )

    def test_bom_has_operations(self):
        bom_1 = self.bom_1
        # check if bom work has some work orders
        self.assertNotEqual(len(bom_1.operation_ids), 0)

    def test_production_create(self):
        production = self.create_production_to_test()

        production.action_confirm()
        self.assertNotEqual(len(production.workorder_ids), 0)

    def test_start_workorder_with_blocking_time(self):
        production = self.create_production_to_test()

        production.action_confirm()

        # start workorder
        workorder = production.workorder_ids[0]
        workorder.button_start()

        # check if work order has blocking stage date set
        # and check if the blocking state date is correct
        # (date_start + recommended_blocking_time)
        self.assertNotEqual(workorder.blocking_stage_end, False)
        self.assertEqual(
            workorder.blocking_stage_end,
            workorder.date_start
            + timedelta(hours=workorder.operation_id.recommended_blocking_time),
        )

    def test_pause_workorder_with_blocking_message(self):
        production = self.create_production_to_test()

        production.action_confirm()

        # start workorder
        workorder = production.workorder_ids[0]
        workorder.button_start()
        self.assertEqual(workorder.is_user_working, True)

        # check if the popup opens when workorder button_pending method is called
        # and the blocking state date is not over
        # (blocking_stage_end > fields.Datetime.now())
        is_popup = workorder.button_pending()
        self.assertIsInstance(is_popup, dict)

        wizard_obj = self.env["mrp.workorder.blocking.reason.wizard"].with_context(
            active_id=workorder.id, action_to_do="button_pending"
        )
        wizard_id = wizard_obj.create(
            {"interruption_reason": "Test reason button_pending"}
        )

        wizard_id.action_confirm()

        # check if work order has blocking_period_interrupted
        # set and a reason
        self.assertNotEqual(workorder.blocking_period_interrupted, False)
        self.assertEqual(workorder.interruption_reason, "Test reason button_pending")

    def test_finish_workorder_with_blocking_message(self):
        production = self.create_production_to_test()

        production.action_confirm()

        # start workorder
        workorder = production.workorder_ids[0]
        workorder.button_start()

        # check if the popup opens when workorder button_finish method is called
        # and the blocking state date is not over
        # (blocking_stage_end > fields.Datetime.now())
        is_popup = workorder.button_finish()
        self.assertIsInstance(is_popup, dict)

        wizard_obj = self.env["mrp.workorder.blocking.reason.wizard"].with_context(
            active_id=workorder.id, action_to_do="button_finish"
        )
        wizard_id = wizard_obj.create(
            {"interruption_reason": "Test reason button_finish"}
        )

        wizard_id.action_confirm()

        # check if work order has blocking_period_interrupted
        # set and a reason
        self.assertNotEqual(workorder.blocking_period_interrupted, False)
        self.assertEqual(workorder.interruption_reason, "Test reason button_finish")
        self.assertEqual(workorder.state, "done")
