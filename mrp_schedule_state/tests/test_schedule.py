# © 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestSchedule(TestMrpCommon):
    def setUp(self):
        super().setUp()

    def test_(self):
        # confirmed order
        mo, _bom, _build_product, component1, component2 = self.generate_mo()
        self.assertEqual(mo.schedule_state, "waiting")
        location = mo.location_src_id
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Test inventory",
                "location_ids": [(6, 0, [location.id])],
                "state": "confirm",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": component1.id,
                            "location_id": location.id,
                            "product_qty": 20,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": component2.id,
                            "location_id": location.id,
                            "product_qty": 5,
                        },
                    ),
                ],
            }
        )
        inventory._action_done()
        mo.action_assign()
        # once raw material is ready, MO is rdy to be scheduled
        self.assertEqual(mo.schedule_state, "todo")

        now_with_margin = datetime.now() + timedelta(minutes=10)
        wizard = (
            self.env["switch.schedule_state"]
            .with_context(active_ids=mo.id)
            .create({"schedule_state": "scheduled", "schedule_date": now_with_margin})
        )
        wizard.switch_schedule_state()
        self.assertEqual(mo.date_planned_start, now_with_margin)
        self.assertEqual(mo.schedule_state, "scheduled")
        self.assertEqual(mo.schedule_date, now_with_margin)
        self.assertEqual(mo.schedule_user_id.id, self.env.user.id)

        wizard = (
            self.env["switch.schedule_state"]
            .with_context(active_ids=mo.id)
            .create({"schedule_state": "todo"})
        )
        wizard.switch_schedule_state()
        self.assertEqual(mo.schedule_state, "todo")
        self.assertFalse(mo.schedule_date)
        self.assertFalse(mo.schedule_user_id)

        mo.button_unreserve()
        # raw material not available anymore, back to waiting
        self.assertEqual(mo.schedule_state, "waiting")

        wizard = (
            self.env["switch.schedule_state"]
            .with_context(active_ids=mo.id)
            .create({"schedule_state": "scheduled", "schedule_date": now_with_margin})
        )
        wizard.switch_schedule_state()
        # scheduling when raw material is not present yet is possible, it should
        # go to scheduled state only when the raw material will be available
        self.assertEqual(mo.schedule_state, "waiting")
        self.assertEqual(mo.schedule_date, now_with_margin)
        self.assertEqual(mo.schedule_user_id.id, self.env.user.id)
        mo.action_assign()
        self.assertEqual(mo.schedule_state, "scheduled")
