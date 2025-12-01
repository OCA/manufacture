# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests.common import tagged
from odoo.tools import misc

from odoo.addons.base.models.ir_actions_report import IrActionsReport
from odoo.addons.quality_control_oca.tests.test_quality_control import (
    TestQualityControlOcaBase,
)


@tagged("post_install", "-at_install")
class TestQualityControlSignOca(TestQualityControlOcaBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.icp = cls.env["ir.config_parameter"].sudo()

        pdf_path = misc.file_path("sign_oca/tests/empty.pdf")

        with open(pdf_path, "rb") as f:
            cls.empty_pdf_bytes = f.read()

        cls.fake_report = cls.env["ir.actions.report"].create(
            {
                "name": "Fake QC Inspection Report",
                "model": "qc.inspection",
                "report_type": "qweb-pdf",
                "report_name": "quality_control_sign_oca.fake_qc_report",
                "print_report_name": "'Fake QC Inspection Report'",
            }
        )

        cls.icp.set_param(
            "quality_control_sign_oca.quality_inspection_report_id",
            str(cls.fake_report.id),
        )

        def fake_render(self_report, report_ref, res_ids=None, data=None):
            return cls.empty_pdf_bytes, "application/pdf"

        cls._pdf_patch = patch.object(IrActionsReport, "_render_qweb_pdf", fake_render)
        cls._pdf_patch.start()

        cls.role_employee = cls.env.ref("sign_oca.sign_role_employee")

        cls.env["qc.sign.template.item"].create(
            {
                "company_id": cls.env.company.id,
                "report_id": cls.fake_report.id,
                "role_id": cls.role_employee.id,
                "page": 1,
                "position_x": 10.0,
                "position_y": 20.0,
                "width": 30.0,
                "height": 10.0,
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls._pdf_patch.stop()
        super().tearDownClass()

    def _build_sign_data(self, signer):
        items = signer.get_info()["items"]
        data = {}
        for key, val in items.items():
            item = val.copy()
            item["value"] = f"Signed by {signer.partner_id.name}"
            data[key] = item
        return data

    def test_get_sign_report_missing_config(self):
        inspection = self.inspection1

        self.icp.set_param(
            "quality_control_sign_oca.quality_inspection_report_id", False
        )

        with self.assertRaises(UserError):
            inspection._get_sign_report()

        self.icp.set_param(
            "quality_control_sign_oca.quality_inspection_report_id",
            str(self.fake_report.id),
        )

    def test_get_signature_positions_by_role(self):
        inspection = self.inspection1

        positions_by_role = inspection._get_signature_positions_by_role(
            self.fake_report
        )
        self.assertIn(self.role_employee, positions_by_role)
        self.assertTrue(positions_by_role[self.role_employee])

    def test_full_inspection_sign_flow(self):
        inspection = self.inspection1

        report = inspection._get_sign_report()
        self.assertEqual(report, self.fake_report)

        action = inspection.with_context(
            force_report_rendering=True
        ).action_sign_inspection()

        self.assertIsInstance(action, dict)
        self.assertEqual(action.get("type"), "ir.actions.act_url")

        self.assertTrue(inspection.sign_request_ids)
        self.assertEqual(inspection.sign_request_count, 1)

        req = inspection.sign_request_ids[0]
        self.assertEqual(req.inspection_id, inspection)
        self.assertEqual(req.record_ref, inspection)

        self.assertEqual(inspection.current_sign_request_id, req)

        inspection.invalidate_recordset()
        self.assertFalse(inspection.signed)

        self.assertTrue(req.signer_ids)
        signer = req.signer_ids[0]
        self.assertEqual(signer.role_id, self.role_employee)

        data = self._build_sign_data(signer)
        res = signer.action_sign(data)
        self.assertEqual(res.get("type"), "ir.actions.act_url")

        req.invalidate_recordset()
        inspection.invalidate_recordset()

        self.assertEqual(req.state, "2_signed")
        self.assertTrue(inspection.signed)

    def test_action_view_sign_requests(self):
        inspection = self.inspection1

        inspection.with_context(force_report_rendering=True).action_sign_inspection()

        self.assertTrue(inspection.sign_request_ids)
        req = inspection.sign_request_ids[0]
        self.assertEqual(req.inspection_id, inspection)

        action = inspection.action_view_sign_requests()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "sign.oca.request")
        self.assertIn("domain", action)
        self.assertIn(("inspection_id", "=", inspection.id), action["domain"])
