# Copyright 2026 CHEF PIXEL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestMrpBomAttributeMatch(TransactionCase):
    def setUp(self):
        super().setUp()
        self.color_attr = self.env["product.attribute"].create({"name": "Color"})
        self.size_attr = self.env["product.attribute"].create({"name": "Size"})

        self.red_val = self.env["product.attribute.value"].create(
            {
                "name": "Red",
                "attribute_id": self.color_attr.id,
            }
        )
        self.small_val = self.env["product.attribute.value"].create(
            {
                "name": "S",
                "attribute_id": self.size_attr.id,
            }
        )

        # =========================
        # 2. Create product template with attributes
        # =========================
        self.tmpl = self.env["product.template"].create(
            {
                "name": "Test Product",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.color_attr.id,
                            "value_ids": [(6, 0, [self.red_val.id])],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.size_attr.id,
                            "value_ids": [(6, 0, [self.small_val.id])],
                        },
                    ),
                ],
            }
        )
        self.tmpl._create_variant_ids()
        self.product_variant = self.tmpl.product_variant_ids[0]

        self.component_tmpl = self.env["product.template"].create(
            {
                "name": "Component Template",
            }
        )
        self.component_tmpl.attribute_line_ids = [
            (
                0,
                0,
                {
                    "attribute_id": self.color_attr.id,
                    "value_ids": [(6, 0, [self.red_val.id])],
                },
            ),
            (
                0,
                0,
                {
                    "attribute_id": self.size_attr.id,
                    "value_ids": [(6, 0, [self.small_val.id])],
                },
            ),
        ]

        self.bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.tmpl.id,
                "type": "normal",
            }
        )
        self.component_line = self.env["mrp.bom.line"].create(
            {
                "bom_id": self.bom.id,
                "component_template_id": self.component_tmpl.id,
                "product_qty": 1.0,
            }
        )

    def test_report_bom_structure_variant(self):
        report = self.env["report.mrp.report_bom_structure"]
        res = report._get_report_data(self.bom.id)
        self.assertFalse(
            res.get("is_variant_applied", False),
            "Expected is_variant_applied to be False before applying variants",
        )

    def test_bom_data_variant_applied(self):
        report = self.env["report.mrp.report_bom_structure"]
        stock_location = self.env["stock.location"].create(
            {
                "name": "Test Location",
                "usage": "internal",
            }
        )
        warehouse = self.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse",
                "code": "TWH",
                "lot_stock_id": stock_location.id,
            }
        )

        data = report._get_bom_data(
            self.bom, warehouse=warehouse, product=self.product_variant
        )

        self.assertTrue(
            data.get("is_variant_applied", False),
            "Expected is_variant_applied to be True when variant is applied",
        )

    def test_bom_line_invalid_attributes(self):
        invalid_tmpl = self.env["product.template"].create(
            {
                "name": "Invalid Component",
            }
        )
        with self.assertRaises(ValidationError):
            self.env["mrp.bom.line"].create(
                {
                    "bom_id": self.bom.id,
                    "component_template_id": invalid_tmpl.id,
                    "product_qty": 1.0,
                }
            )
