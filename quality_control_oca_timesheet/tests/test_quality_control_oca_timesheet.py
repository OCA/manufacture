# Copyright 2024 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase


class TestQcInspectionTimesheetTotalHours(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.qc_inspection = cls.env["qc.inspection"].create(
            {
                "name": "Test Inspection",
            }
        )

    def test_no_timesheets(self):
        """Test total hours when no timesheets are associated"""
        self.assertEqual(
            self.qc_inspection.timesheet_total_hours,
            0,
            "Total hours should be 0 when there are no timesheets.",
        )

    def test_one_timesheet(self):
        """Test total hours with one timesheet"""
        self.env["account.analytic.line"].create(
            {
                "qc_inspection_id": self.qc_inspection.id,
                "unit_amount": 5.0,
                "name": "Timesheet 1",
            }
        )

        self.qc_inspection._compute_timesheet_total_hours()

        self.assertEqual(
            self.qc_inspection.timesheet_total_hours,
            5.0,
            "Total hours should be 5 with one timesheet entry.",
        )

    def test_multiple_timesheets(self):
        """Test total hours with multiple timesheets"""
        self.env["account.analytic.line"].create(
            {
                "qc_inspection_id": self.qc_inspection.id,
                "unit_amount": 3.0,
                "name": "Timesheet 1",
            }
        )
        self.env["account.analytic.line"].create(
            {
                "qc_inspection_id": self.qc_inspection.id,
                "unit_amount": 2.5,
                "name": "Timesheet 2",
            }
        )
        self.env["account.analytic.line"].create(
            {
                "qc_inspection_id": self.qc_inspection.id,
                "unit_amount": 1.5,
                "name": "Timesheet 3",
            }
        )

        self.qc_inspection._compute_timesheet_total_hours()

        self.assertEqual(
            self.qc_inspection.timesheet_total_hours,
            7.0,
            "Total hours should be 7 (3 + 2.5 + 1.5) with multiple timesheets.",
        )
