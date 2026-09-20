# Copyright 2026 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestMrpUnbuildSourceLocation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse",
                "code": "TWH",
            }
        )
        cls.location_1 = cls.env["stock.location"].create(
            {
                "name": "Location 1",
                "location_id": cls.warehouse.lot_stock_id.id,
                "usage": "internal",
            }
        )
        cls.location_2 = cls.env["stock.location"].create(
            {
                "name": "Location 2",
                "location_id": cls.warehouse.lot_stock_id.id,
                "usage": "internal",
            }
        )
        cls.product_lot = cls.env["product.product"].create(
            {"name": "Lot Product", "type": "product", "tracking": "lot"}
        )
        cls.product_none = cls.env["product.product"].create(
            {"name": "No Tracking Product", "type": "product", "tracking": "none"}
        )
        cls.lot_1 = cls.env["stock.lot"].create(
            {"name": "lot_1", "product_id": cls.product_lot.id}
        )
        cls.lot_2 = cls.env["stock.lot"].create(
            {"name": "lot_2", "product_id": cls.product_lot.id}
        )
        cls.lot_3 = cls.env["stock.lot"].create(
            {"name": "lot_3", "product_id": cls.product_lot.id}
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_lot, cls.location_1, 5, lot_id=cls.lot_1
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_lot, cls.location_1, 2, lot_id=cls.lot_2
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_lot, cls.location_2, 3, lot_id=cls.lot_2
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_none, cls.location_1, 10
        )

    def test_product_domain_no_lot(self):
        unbuild = self.env["mrp.unbuild"].create({"product_id": self.product_lot.id})
        locations = self.env["stock.location"].search(unbuild.location_domain)
        self.assertIn(self.location_1, locations)
        self.assertIn(self.location_2, locations)

    def test_product_no_tracking_auto_select(self):
        unbuild = self.env["mrp.unbuild"].create({"product_id": self.product_none.id})
        self.assertEqual(unbuild.location_id, self.location_1)

    def test_lot_single_location_auto_select(self):
        unbuild = self.env["mrp.unbuild"].create({"product_id": self.product_lot.id})
        unbuild.lot_id = self.lot_1
        self.assertEqual(unbuild.location_id, self.location_1)

    def test_lot_multiple_locations(self):
        unbuild = self.env["mrp.unbuild"].create({"product_id": self.product_lot.id})
        unbuild.lot_id = self.lot_2
        locations = self.env["stock.location"].search(unbuild.location_domain)
        self.assertIn(self.location_1, locations)
        self.assertIn(self.location_2, locations)

    def test_lot_no_stock_raises_error(self):
        unbuild = self.env["mrp.unbuild"].create({"product_id": self.product_lot.id})
        with self.assertRaises(ValidationError):
            unbuild.lot_id = self.lot_3
