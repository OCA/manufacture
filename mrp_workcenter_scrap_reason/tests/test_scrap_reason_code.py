# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class StockScrap(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.categ_1 = cls.env.ref("product.product_category_all")
        cls.categ_2 = cls.env["product.category"].create({"name": "Test category"})
        stock_location_locations_virtual = cls.env["stock.location"].create(
            {"name": "Virtual Locations", "usage": "view", "posz": 1}
        )
        cls.scrapped_location = cls.env["stock.location"].create(
            {
                "name": "Scrapped",
                "location_id": stock_location_locations_virtual.id,
                "scrap_location": True,
                "usage": "inventory",
            }
        )

        cls.scrap_product = cls.env["product.product"].create(
            {
                "name": "Scrap Product A",
                "type": "consu",
                "is_storable": True,
                "categ_id": cls.categ_1.id,
            }
        )
        cls.scrap_product_2 = cls.env["product.product"].create(
            {
                "name": "Scrap Product A",
                "type": "consu",
                "is_storable": True,
                "categ_id": cls.categ_2.id,
            }
        )

        cls.reason_code = cls.env["scrap.reason.code"].create(
            {
                "name": "DM300",
                "description": "Product is damage",
                "location_id": cls.scrapped_location.id,
            }
        )
        cls.reason_code_only_categ_2 = cls.env["scrap.reason.code"].create(
            {
                "name": "Test Code 2",
                "description": "Test description",
                "product_category_ids": [(6, 0, cls.categ_2.ids)],
            }
        )
        cls.workcenter_1 = cls.env["mrp.workcenter"].create(
            {
                "name": "WC Test 1",
            }
        )

        cls.workcenter_2 = cls.env["mrp.workcenter"].create(
            {
                "name": "WC Test 2",
            }
        )

        cls.reason_code_wc1 = cls.env["scrap.reason.code"].create(
            {
                "name": "WC1 Code",
                "mrp_workcenter_ids": [(6, 0, cls.workcenter_1.ids)],
            }
        )

        cls.reason_code_wc2 = cls.env["scrap.reason.code"].create(
            {
                "name": "WC2 Code",
                "mrp_workcenter_ids": [(6, 0, cls.workcenter_2.ids)],
            }
        )
        cls.finished_product = cls.env["product.product"].create(
            {
                "name": "Finished Product",
                "type": "consu",
                "is_storable": True,
                "categ_id": cls.categ_1.id,
            }
        )

        cls.component_product = cls.env["product.product"].create(
            {
                "name": "Component Product",
                "type": "consu",
                "is_storable": True,
                "categ_id": cls.categ_1.id,
            }
        )

        cls.test_bom_1 = cls.env["mrp.bom"].create(
            {
                "product_id": cls.finished_product.id,
                "product_tmpl_id": cls.finished_product.product_tmpl_id.id,
                "product_uom_id": cls.finished_product.uom_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )

        cls.env["mrp.bom.line"].create(
            {
                "bom_id": cls.test_bom_1.id,
                "product_id": cls.component_product.id,
                "product_qty": 1.0,
            }
        )

        cls.mo_1 = cls.env["mrp.production"].create(
            {
                "name": "MO ABC",
                "product_id": cls.finished_product.id,
                "product_uom_id": cls.finished_product.uom_id.id,
                "product_qty": 2,
                "bom_id": cls.test_bom_1.id,
                "location_src_id": cls.stock_location.id,
                "location_dest_id": cls.stock_location.id,
            }
        )

        cls.workorder = cls.env["mrp.workorder"].create(
            {
                "name": "Workorder Test",
                "production_id": cls.mo_1.id,
                "product_uom_id": cls.finished_product.uom_id.id,
                "workcenter_id": cls.workcenter_1.id,
                "qty_remaining": 1,
            }
        )

    def test_allowed_reason_codes(self):
        # INVALID BY CATEGORY (no workorder assigned)
        with self.assertRaises(ValidationError):
            self.env["stock.scrap"].create(
                {
                    "product_id": self.scrap_product.id,  # belongs to category 1
                    "product_uom_id": self.scrap_product.uom_id.id,
                    "scrap_qty": 1,
                    "reason_code_id": self.reason_code_only_categ_2.id,
                    # only allowed for category 2
                }
            )

        # NVALID BY WORKCENTER
        with self.assertRaises(ValidationError):
            self.env["stock.scrap"].create(
                {
                    "product_id": self.scrap_product.id,
                    "product_uom_id": self.scrap_product.uom_id.id,
                    "scrap_qty": 1,
                    "workorder_id": self.workorder.id,  # assigned to WC1
                    "reason_code_id": self.reason_code_wc2.id,  # WC2 is not allowed
                }
            )

        # VALID BY WORKCENTER (even if category does not match)
        scrap = self.env["stock.scrap"].create(
            {
                "product_id": self.scrap_product.id,  # category 1
                "product_uom_id": self.scrap_product.uom_id.id,
                "scrap_qty": 1,
                "workorder_id": self.workorder.id,  # WC1
                "reason_code_id": self.reason_code_wc1.id,  # allowed by WC
            }
        )
        self.assertIn(self.reason_code_wc1, scrap.allowed_reason_code_ids)

        # VALID BY BOTH CATEGORY AND WORKCENTER
        scrap = self.env["stock.scrap"].create(
            {
                "product_id": self.scrap_product_2.id,  # category 2
                "product_uom_id": self.scrap_product_2.uom_id.id,
                "scrap_qty": 1,
                "workorder_id": self.workorder.id,  # WC1
                "reason_code_id": self.reason_code_only_categ_2.id,
                # allowed by category
            }
        )

        allowed = scrap.allowed_reason_code_ids
        self.assertIn(self.reason_code_wc1, allowed)  # allowed by WC
        self.assertIn(self.reason_code_only_categ_2, allowed)  # allowed by category
        self.assertNotIn(self.reason_code_wc2, allowed)  # WC2 should not be included
