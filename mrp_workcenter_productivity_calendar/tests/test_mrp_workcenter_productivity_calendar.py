# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.fields import Command
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon

# 2026-08-11 is a Tuesday.
TUESDAY = "1"


class TestMrpWorkcenterProductivityCalendar(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.calendar = cls.env["resource.calendar"].create(
            {
                "name": "Test Shift Calendar",
                "tz": "UTC",
                "attendance_ids": [
                    Command.create(
                        {
                            "name": "Tuesday Morning",
                            "dayofweek": TUESDAY,
                            "hour_from": 8,
                            "hour_to": 12,
                        }
                    ),
                    Command.create(
                        {
                            "name": "Tuesday Afternoon",
                            "dayofweek": TUESDAY,
                            "hour_from": 13,
                            "hour_to": 17,
                        }
                    ),
                ],
            }
        )
        cls.workcenter_enabled = cls.env["mrp.workcenter"].create(
            {
                "name": "Test Workcenter Calendar Duration Enabled",
                "resource_calendar_id": cls.calendar.id,
                "use_calendar_for_duration": True,
            }
        )
        cls.workcenter_disabled = cls.env["mrp.workcenter"].create(
            {
                "name": "Test Workcenter Calendar Duration Disabled",
                "resource_calendar_id": cls.calendar.id,
                "use_calendar_for_duration": False,
            }
        )
        cls.workcenter_without_calendar = cls.env["mrp.workcenter"].create(
            {
                "name": "Test Workcenter No Calendar",
                "resource_calendar_id": False,
                "use_calendar_for_duration": True,
            }
        )
        cls.productivity_view = cls.env["ir.ui.view"].create(
            {
                "name": "Test mrp.workcenter.productivity form",
                "model": "mrp.workcenter.productivity",
                "arch": """
                    <form>
                        <field name="workcenter_id"/>
                        <field name="loss_id"/>
                        <field name="date_start"/>
                        <field name="date_end"/>
                        <field name="duration" readonly="id"/>
                    </form>
                """,
            }
        )

    def _create_productivity(
        self,
        workcenter,
        loss_xmlid,
        date_start=datetime(2026, 8, 11, 10, 0, 0),
        date_end=datetime(2026, 8, 11, 14, 0, 0),
    ):
        return self.env["mrp.workcenter.productivity"].create(
            {
                "workcenter_id": workcenter.id,
                "loss_id": self.env.ref(loss_xmlid).id,
                "date_start": date_start,
                "date_end": date_end,
            }
        )

    def _form(self, workcenter):
        form = Form(
            self.env["mrp.workcenter.productivity"], view=self.productivity_view
        )
        form.workcenter_id = workcenter
        form.loss_id = self.env.ref("mrp.block_reason7")
        return form

    def test_productive_time_deducts_calendar_break_when_enabled(self):
        productivity = self._create_productivity(
            self.workcenter_enabled, "mrp.block_reason7"
        )
        self.assertAlmostEqual(productivity.duration, 180.0, places=2)

    def test_productive_time_keeps_raw_elapsed_time_when_disabled(self):
        productivity = self._create_productivity(
            self.workcenter_disabled, "mrp.block_reason7"
        )
        self.assertAlmostEqual(productivity.duration, 240.0, places=2)

    def test_productive_time_without_calendar_keeps_raw_elapsed_time(self):
        productivity = self._create_productivity(
            self.workcenter_without_calendar, "mrp.block_reason7"
        )
        self.assertAlmostEqual(productivity.duration, 240.0, places=2)

    def test_non_productive_time_uses_calendar_regardless_of_flag(self):
        productivity = self._create_productivity(
            self.workcenter_disabled, "mrp.block_reason0"
        )
        self.assertAlmostEqual(productivity.duration, 180.0, places=2)

    def test_activity_ending_exactly_at_lunch_boundary(self):
        productivity = self._create_productivity(
            self.workcenter_enabled,
            "mrp.block_reason7",
            date_start=datetime(2026, 8, 11, 8, 0, 0),
            date_end=datetime(2026, 8, 11, 13, 0, 0),
        )
        self.assertAlmostEqual(productivity.duration, 240.0, places=2)

    def test_manual_dates_are_not_overridden_when_calendar_enabled(self):
        with self._form(self.workcenter_enabled) as form:
            form.date_start = datetime(2026, 8, 11, 10, 0, 0)
            form.date_end = datetime(2026, 8, 11, 14, 0, 0)
        productivity = form.save()
        self.assertEqual(productivity.date_start, datetime(2026, 8, 11, 10, 0, 0))
        self.assertEqual(productivity.date_end, datetime(2026, 8, 11, 14, 0, 0))
        self.assertAlmostEqual(productivity.duration, 180.0, places=2)

    def test_dates_still_recompute_each_other_when_calendar_disabled(self):
        with self._form(self.workcenter_disabled) as form:
            form.date_start = datetime(2026, 8, 11, 9, 0, 0)
            form.date_end = datetime(2026, 8, 11, 12, 0, 0)
        productivity = form.save()
        self.assertEqual(productivity.date_start, datetime(2026, 8, 11, 9, 0, 0))
        self.assertEqual(productivity.date_end, datetime(2026, 8, 11, 12, 0, 0))

    def test_duration_recomputes_date_start_when_calendar_disabled(self):
        with self._form(self.workcenter_disabled) as form:
            form.date_end = datetime(2026, 8, 11, 14, 0, 0)
            form.duration = 120.0
            self.assertEqual(form.date_start, datetime(2026, 8, 11, 12, 0, 0))

    def test_duration_does_not_recompute_date_start_when_calendar_enabled(self):
        with self._form(self.workcenter_enabled) as form:
            form.date_end = datetime(2026, 8, 11, 14, 0, 0)
            initial_date_start = form.date_start
            form.duration = 120.0
            self.assertEqual(form.date_start, initial_date_start)
