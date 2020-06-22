# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestManufacturingOrderType(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Picking Types
        picking_type_id = cls.env["stock.picking.type"].search(
            [("code", "=", "mrp_operation")], limit=1
        )
        # MO Type
        cls.type1 = cls.env["manufacturing.order.type"].create({"name": "Type 1"})
        cls.type2 = cls.env["manufacturing.order.type"].create(
            {"name": "Type 2", "picking_type_id": picking_type_id.id}
        )
        # Products
        cls.product = cls.env.ref("mrp.product_product_computer_desk")
        cls.product.mo_type_id = cls.type2
        cls.bom = cls.env.ref("mrp.mrp_bom_desk")
        # Location
        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "X Warehouse", "code": "X WH"}
        )
        cls.loc_stock = cls.warehouse.lot_stock_id

    def test_manufacturing_order_type(self):
        mo = self.env["mrp.production"].create(
            {
                "mo_type_id": self.type1.id,
                "product_id": self.product.id,
                "bom_id": self.bom.id,
                "location_src_id": self.loc_stock.id,
                "location_dest_id": self.loc_stock.id,
                "product_qty": 1,
                "product_uom_id": self.product.uom_id.id,
            }
        )
        self.assertEquals(mo.mo_type_id, self.type1)
        mo.onchange_product_id()
        self.assertEquals(mo.mo_type_id, self.type2)
        mo._onchange_mo_type_id()
        self.assertEquals(mo.picking_type_id, self.type2.picking_type_id)
