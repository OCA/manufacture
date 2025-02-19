from odoo.addons.base.tests.common import BaseCommon


class TestMrpBomLocation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.picking_type = cls.env.ref("stock.picking_type_internal")

        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.env["product.template"]
                .create({"name": "Test Product"})
                .id,
                "picking_type_id": cls.picking_type.id,
            }
        )

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
