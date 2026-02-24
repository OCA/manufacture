# Copyright 2026 CHEF PIXEL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import Command
from odoo.exceptions import UserError, ValidationError

from .common import TestMrpBomAttributeMatchBase


class TestMrpBomAttributeMatch(TestMrpBomAttributeMatchBase):
    def setUp(self):
        super().setUp()
        self.tmpl = self.env["product.template"].create(
            {
                "name": "Test Product",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.product_attribute.id,
                            "value_ids": [
                                Command.set([self.attribute_value_ids[0].id])
                            ],
                        },
                    ),
                ],
            }
        )
        self.product_variant = self.tmpl.product_variant_ids[0]

    def test_bom_data_variant_applied(self):
        """Tests report data and unconditional warehouse creation."""
        report = self.env["report.mrp.report_bom_structure"]
        warehouse = self.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse",
                "code": "TWH",
            }
        )
        data = report._get_bom_data(
            self.bom_id, warehouse=warehouse, product=self.product_variant
        )
        self.assertTrue(data.get("is_variant_applied"))

    def test_bom_recursion_error(self):
        """Triggers recursion check_cycle and recStack logic."""
        with self.assertRaises(UserError):
            self._create_bom(
                self.product_9, [{"product_id": self.product_9, "product_qty": 1.0}]
            )

    def test_invalid_attribute_validation(self):
        """Triggers ValidationError for attribute mismatch."""
        with self.assertRaises(ValidationError):
            self.env["mrp.bom.line"].create(
                {
                    "bom_id": self.bom_id.id,
                    "component_template_id": self.product_10.product_tmpl_id.id,
                    "product_qty": 1.0,
                }
            )
