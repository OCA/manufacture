# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestMrpAutoCreateLot(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestMrpAutoCreateLot, cls).setUpClass()
        cls.production_model = cls.env["mrp.production"]
        cls.bom_model = cls.env["mrp.bom"]
        cls.picking_model = cls.env["stock.picking"]
        cls.stock_location_stock = cls.env.ref("stock.stock_location_stock")
        cls.manufacture_route = cls.env.ref("mrp.route_warehouse0_manufacture")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

        cls.manufacture_picking_type = cls.env["stock.picking.type"].search(
            [("code", "=", "mrp_operation")], limit=1
        )
        cls.manufacture_picking_type.auto_create_lot = True
        cls.product_manuf = cls.env["product.product"].create(
            {
                "name": "Manuf",
                "type": "product",
                "uom_id": cls.uom_unit.id,
                "route_ids": [(6, 0, cls.manufacture_route.ids)],
                "tracking": "lot",
                "auto_create_lot": True,
            }
        )

        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_id": cls.product_manuf.id,
                "product_tmpl_id": cls.product_manuf.product_tmpl_id.id,
                "type": "normal",
            }
        )

    def test_01_manufacture_auto_create_lot(self):
        production = self.production_model.create(
            {
                "product_id": self.product_manuf.id,
                "product_qty": 1,
                "product_uom_id": self.uom_unit.id,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        production.qty_producing = 1
        production.button_mark_done()
        self.assertTrue(production.lot_producing_id)

    def test_02_manufacture_auto_create_lot_existing_lot(self):
        """If a lot has already been assigned, it should not be changed"""
        production = self.production_model.create(
            {
                "product_id": self.product_manuf.id,
                "product_qty": 1,
                "product_uom_id": self.uom_unit.id,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        production.lot_producing_id = self.env["stock.lot"].create(
            {"product_id": self.product_manuf.id, "name": "TEST"}
        )
        production.qty_producing = 1
        production.button_mark_done()
        self.assertEqual(production.lot_producing_id.name, "TEST")

    def test_03_manufacture_auto_create_lot_no_auto_create(self):
        """If the product has auto create lot set to False, no lot
        should be auto created"""
        self.product_manuf.auto_create_lot = False
        production = self.production_model.create(
            {
                "product_id": self.product_manuf.id,
                "product_qty": 1,
                "product_uom_id": self.uom_unit.id,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        production.qty_producing = 1
        with self.assertRaises(UserError):
            production.button_mark_done()
        self.assertFalse(production.lot_producing_id.name)

    def test_04_manufacture_auto_create_lot_no_qty(self):
        """If no quantities have been produced, a lot should not be
        automatically created"""
        production = self.production_model.create(
            {
                "product_id": self.product_manuf.id,
                "product_qty": 1,
                "product_uom_id": self.uom_unit.id,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        production.button_mark_done()
        self.assertFalse(production.lot_producing_id.name)

    def test_05_manufacture_auto_create_lot_no_tracking(self):
        """If the product is not tracked, the lot should not be automatically created"""
        self.product_manuf.tracking = "none"
        production = self.production_model.create(
            {
                "product_id": self.product_manuf.id,
                "product_qty": 1,
                "product_uom_id": self.uom_unit.id,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        production.qty_producing = 1
        production.button_mark_done()
        self.assertFalse(production.lot_producing_id.name)

    def test_06_manufacture_auto_create_lot_no_auto_create_in_operation(self):
        """If the operation type has "Auto Create Lot" to false,
        the lot should not be automatically created"""
        self.manufacture_picking_type.auto_create_lot = False
        production = self.production_model.create(
            {
                "product_id": self.product_manuf.id,
                "product_qty": 1,
                "product_uom_id": self.uom_unit.id,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        production.qty_producing = 1
        with self.assertRaises(UserError):
            production.button_mark_done()
        self.assertFalse(production.lot_producing_id.name)
