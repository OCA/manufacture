# Copyright 2026 FactorLibre - Daniel Amores
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.quality_control_oca.tests.test_quality_control import (
    TestQualityControlOcaBase,
)


@tagged("post_install", "-at_install")
class TestInspectionCompany(TestQualityControlOcaBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env.company
        cls.company_b = cls.env["res.company"].create({"name": "Company B"})

    def _get_trigger_line(self, product):
        product.qc_triggers = [
            (0, 0, {"trigger": self.qc_trigger.id, "test": self.test.id})
        ]
        return product.qc_triggers

    def test_inspection_company_from_origin_document(self):
        """The inspection takes the company of the origin document."""
        product = self.env["product.product"].create(
            {"name": "Product B", "company_id": self.company_b.id}
        )
        trigger_line = self._get_trigger_line(product)
        inspection = (
            self.env["qc.inspection"]
            .with_company(self.company_a)
            ._make_inspection(product, trigger_line)
        )
        self.assertEqual(inspection.company_id, self.company_b)

    def test_inspection_company_default_without_origin_company(self):
        """Without origin company the inspection keeps the active company."""
        product = self.env["product.product"].create(
            {"name": "Product without company", "company_id": False}
        )
        trigger_line = self._get_trigger_line(product)
        inspection = (
            self.env["qc.inspection"]
            .with_company(self.company_a)
            ._make_inspection(product, trigger_line)
        )
        self.assertEqual(inspection.company_id, self.company_a)

    def test_inspection_company_header_override_respected(self):
        """A company already set in the inspection header is not replaced."""
        product = self.env["product.product"].create(
            {"name": "Product B", "company_id": self.company_b.id}
        )
        trigger_line = self._get_trigger_line(product)
        inspection_class = type(self.env["qc.inspection"])
        prepare_header = inspection_class._prepare_inspection_header

        def prepare_header_with_company(inspection, object_ref, line):
            header = prepare_header(inspection, object_ref, line)
            header["company_id"] = self.company_a.id
            return header

        with patch.object(
            inspection_class,
            "_prepare_inspection_header",
            prepare_header_with_company,
        ), patch.object(
            inspection_class,
            "set_test",
            lambda inspection, line, force_fill=False: None,
        ):
            inspection = self.env["qc.inspection"]._make_inspection(
                product, trigger_line
            )
        self.assertEqual(inspection.company_id, self.company_a)

    def test_inspection_company_hook_without_company_field(self):
        """Origin documents without company give no inspection company."""
        inspection_model = self.env["qc.inspection"]
        country = self.env["res.country"].search([], limit=1)
        self.assertFalse(inspection_model._get_inspection_company(country))
        self.assertFalse(
            inspection_model._get_inspection_company(self.env["product.product"])
        )
