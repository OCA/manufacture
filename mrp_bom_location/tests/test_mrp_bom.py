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
        """Check _get_bom_data and _get_component_data methods."""
        report = self.env["report.mrp.report_bom_structure"]

        self.assertEqual(self.bom.location_id, self.location)

        res = report._get_bom_data(self.bom, self.warehouse)
        self.assertEqual(res["location"], self.location.complete_name)
        for comp in res.get("components", []):
            if comp["product_id"] == self.component_product.id:
                self.assertEqual(comp["location_id"], self.location)

        parent_bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.env["product.template"]
                .create({"name": "Parent Product"})
                .id,
                "picking_type_id": self.picking_type.id,
            }
        )
        res_with_parent = report._get_bom_data(
            self.bom, self.warehouse, parent_bom=parent_bom
        )
        self.assertEqual(
            res_with_parent["location"], parent_bom.location_id.complete_name
        )

        bom_no_loc = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.env["product.template"]
                .create({"name": "No Loc Product"})
                .id,
            }
        )
        self.env["mrp.bom.line"].create(
            {
                "bom_id": bom_no_loc.id,
                "product_id": self.component_product.id,
                "product_qty": 1.0,
            }
        )
        res_no_loc = report._get_bom_data(bom_no_loc, self.warehouse)
        self.assertEqual(res_no_loc["location"], "")
        for comp in res_no_loc.get("components", []):
            if comp["product_id"] == self.component_product.id:
                self.assertEqual(comp["location_id"], "")

        res_parent_no_loc = report._get_bom_data(
            self.bom, self.warehouse, parent_bom=bom_no_loc
        )
        self.assertEqual(res_parent_no_loc["location"], self.location.complete_name)

        product_info = {
            self.component_product.id: {
                "consumptions": {"in_stock": 0},
                self.bom.id: {"route_type": "manufacture", "manufacture_delay": 1},
            }
        }
        res_component = report._get_component_data(
            parent_bom=self.bom,
            product=self.product,
            warehouse=self.warehouse,
            bom_line=self.bom_line,
            line_quantity=1.0,
            level=1,
            index=0,
            product_info=product_info,
        )
        self.assertEqual(res_component["location"], self.location.complete_name)

        res_component_no_loc = report._get_component_data(
            parent_bom=bom_no_loc,
            product=self.product,
            warehouse=self.warehouse,
            bom_line=self.bom_line,
            line_quantity=1.0,
            level=1,
            index=0,
            product_info=product_info,
        )
        self.assertEqual(res_component_no_loc["location"], "")

    def test_bom_structure_report_get_pdf_line(self):
        """Check _get_pdf_line method."""
        report = self.env["report.mrp.report_bom_structure"]

        res_pdf = report._get_pdf_line(self.bom.id, unfolded=True)
        component_line = next(
            (
                line
                for line in res_pdf["lines"]
                if line["name"] == self.component_product.display_name
            ),
            None,
        )
        self.assertIsNotNone(component_line)
        self.assertEqual(component_line["location_name"], self.location.complete_name)

        bom_no_loc = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product_tmpl.id,
            }
        )
        self.env["mrp.bom.line"].create(
            {
                "bom_id": bom_no_loc.id,
                "product_id": self.component_product.id,
                "product_qty": 1.0,
            }
        )
        res_pdf_no_loc = report._get_pdf_line(bom_no_loc.id, unfolded=True)
        component_line_no_loc = next(
            (
                line
                for line in res_pdf_no_loc["lines"]
                if line["name"] == self.component_product.display_name
            ),
            None,
        )
        self.assertIsNotNone(component_line_no_loc)
        self.assertEqual(component_line_no_loc["location_name"], "")
