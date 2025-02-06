# Copyright 2025 Edilio Escalona Almira - Binhexteam
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.exceptions import ValidationError

from odoo.addons.quality_control_oca.tests.test_quality_control import (
    TestQualityControlOcaBase,
)


class TestQualityControlAttachmentOca(TestQualityControlOcaBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.QcTest = cls.env["qc.test"]
        cls.qc_test_id = cls.QcTest.create(
            {"name": "Test required documents", "is_required_attachment": True}
        )

        cls.attachment_ids = cls.env["ir.attachment"].create(
            [
                {
                    "name": "%02d.txt" % idx,
                    "datas": base64.b64encode(b"Att%02d" % idx),
                }
                for idx in range(1)
            ]
        )

        cls.inspection2 = cls.inspection_model.create(
            {
                "name": "Test Inspection required documents",
                "test": cls.qc_test_id.id,
            }
        )

    def test_required_documents(self):
        self.assertRaises(
            ValidationError, self.inspection2.write, {"attachment_ids": []}
        )
        self.assertTrue(
            self.inspection2.with_context(qc_inspection_set_test=True).write(
                {"attachment_ids": []}
            )
        )
        self.inspection2.write({"attachment_ids": [(6, 0, self.attachment_ids.ids)]})
        self.assertGreater(len(self.inspection2.attachment_ids), 0)
        self.assertTrue(self.qc_test_id.is_required_attachment)
        self.qc_test_id.is_required_attachment = False
        self.assertFalse(self.qc_test_id.is_required_attachment)
