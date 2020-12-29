# © 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestSchedule(TestMrpCommon):
    def setUp(self):
        super().setUp()

    def test_(self):
        # confirmed order
        mo = self.generate_mo()[0]
        now_with_margin = datetime.now() + timedelta(minutes=10)
        wizard = (
            self.env["switch.schedule_state"]
            .with_context(active_ids=mo.id)
            .create(
                {"schedule_state": "scheduled", "date_planned_start": now_with_margin}
            )
        )
        wizard.switch_schedule_state()
        self.assertEqual(mo.date_planned_start, now_with_margin)
