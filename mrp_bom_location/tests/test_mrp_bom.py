# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.addons.base.tests.common import BaseCommon


class TestMrpBomLocation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.picking_type = cls.env.ref("stock.picking_type_internal")

        cls.product_tmpl = cls.env["product.template"].create({"name": "Test Product"})
        cls.product = cls.product_tmpl.product_variant_id
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_tmpl.id,
                "picking_type_id": cls.picking_type.id,
            }
        )

        cls.component_product = cls.env["product.product"].create(
            {"name": "Test Component"}
        )
        cls.bom_line = cls.env["mrp.bom.line"].create(
            {
                "bom_id": cls.bom.id,
                "product_id": cls.component_product.id,
                "product_qty": 1.0,
            }
        )

        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)

    def test_location_id_computed(self):
        """Check that location_id in mrp.bom is correctly computed."""
        self.assertEqual(self.bom.location_id, self.location)

    def test_location_id_no_picking_type(self):
        """Check the case where there is no picking_type_id."""
        bom_no_picking = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.env["product.template"]
                .create({"name": "Test Product No Picking"})
                .id,
            }
        )
        self.assertFalse(bom_no_picking.location_id)

    def test_bom_line_location_id(self):
        """Check that location_id in mrp.bom.line is computed"""
        bom_line = self.env["mrp.bom.line"].create(
            {
                "bom_id": self.bom.id,
                "product_id": self.env["product.product"]
                .create({"name": "Test Product Line"})
                .id,
                "product_qty": 10,
            }
        )
        self.assertEqual(
            bom_line.location_id,
            self.bom.location_id,
        )

    def test_bom_structure_report_get_bom_data(self):
        """Check that BoM structure data includes location information."""
        report = self.env["report.mrp.report_bom_structure"]

        result = report._get_bom_data(self.bom, self.warehouse)

        self.assertEqual(result["location"], self.location.complete_name)

        component = next(
            (
                item
                for item in result["components"]
                if item["product_id"] == self.component_product.id
            ),
            None,
        )
        self.assertIsNotNone(component)
        self.assertEqual(component["location_id"], self.location)

        parent_bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.env["product.template"]
                .create({"name": "Parent Product"})
                .id,
                "picking_type_id": self.picking_type.id,
            }
        )

        result = report._get_bom_data(
            self.bom,
            self.warehouse,
            parent_bom=parent_bom,
        )

        self.assertEqual(
            result["location"],
            parent_bom.location_id.complete_name,
        )

        bom_without_location = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.env["product.template"]
                .create({"name": "Product Without Location"})
                .id,
            }
        )

        self.env["mrp.bom.line"].create(
            {
                "bom_id": bom_without_location.id,
                "product_id": self.component_product.id,
                "product_qty": 1,
            }
        )

        result = report._get_bom_data(
            bom_without_location,
            self.warehouse,
        )

        self.assertEqual(result["location"], "")

        component = next(
            (
                item
                for item in result["components"]
                if item["product_id"] == self.component_product.id
            ),
            None,
        )
        self.assertIsNotNone(component)
        self.assertEqual(component["location_id"], "")

        result = report._get_bom_data(
            self.bom,
            self.warehouse,
            parent_bom=bom_without_location,
        )

        self.assertEqual(
            result["location"],
            self.location.complete_name,
        )

    def test_bom_structure_report_get_pdf_line(self):
        """Check that PDF report lines include the expected location."""
        report = self.env["report.mrp.report_bom_structure"]

        result = report._get_pdf_line(
            self.bom.id,
            unfolded=True,
        )

        component = next(
            (
                line
                for line in result["lines"]
                if line["name"] == self.component_product.display_name
            ),
            None,
        )

        self.assertIsNotNone(component)
        self.assertEqual(
            component["location_name"],
            self.location.complete_name,
        )

        bom_without_location = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product_tmpl.id,
            }
        )

        self.env["mrp.bom.line"].create(
            {
                "bom_id": bom_without_location.id,
                "product_id": self.component_product.id,
                "product_qty": 1,
            }
        )

        result = report._get_pdf_line(
            bom_without_location.id,
            unfolded=True,
        )

        component = next(
            (
                line
                for line in result["lines"]
                if line["name"] == self.component_product.display_name
            ),
            None,
        )

        self.assertIsNotNone(component)
        self.assertEqual(component["location_name"], "")
