# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestManufacturingOrderType(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mo_obj = cls.env["mrp.production"]
        cls.company_obj = cls.env["res.company"]
        # Picking Types
        picking_type_id = cls.env["stock.picking.type"].search(
            [("code", "=", "mrp_operation")], limit=1
        )
        # MO Type
        cls.type1 = cls.env["mrp.production.type"].create({"name": "Type 1"})
        cls.type2 = cls.env["mrp.production.type"].create(
            {"name": "Type 2", "picking_type_id": picking_type_id.id}
        )
        cls.type3 = cls.env.ref("mrp_production_type.mo_type_normal")
        # Products
        cls.product = cls.env.ref("mrp.product_product_computer_desk")
        cls.product.mo_type_id = cls.type2
        cls.bom = cls.env.ref("mrp.mrp_bom_desk")
        cls.company2 = cls.company_obj.create({"name": "company2"})
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

    def test_manufacturing_order_change_company(self):
        order = self.mo_obj.new(
            {"product_id": self.product.id, "mo_type_id": self.type3.id}
        )
        self.assertEqual(order.mo_type_id, self.type3)
        order._onchange_company()
        self.assertFalse(order.mo_type_id)

    def test_manufacturing_order_type_company_error(self):
        order = self.mo_obj.create(
            {
                "mo_type_id": self.type3.id,
                "product_id": self.product.id,
                "bom_id": self.bom.id,
                "location_src_id": self.loc_stock.id,
                "location_dest_id": self.loc_stock.id,
                "product_qty": 1,
                "product_uom_id": self.product.uom_id.id,
            }
        )
        self.assertEqual(order.mo_type_id, self.type3)
        self.assertEqual(order.company_id, self.type3.company_id)
        with self.assertRaises(ValidationError):
            order.write({"company_id": self.company2.id})
