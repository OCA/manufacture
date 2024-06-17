# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestStockRepairOrder(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.repair_model = cls.env["repair.order"]
        cls.repair_line_model = cls.env["repair.line"]
        cls.product_model = cls.env["product.product"]
        cls.stock_location_model = cls.env["stock.location"]
        cls.warehouse_model = cls.env["stock.warehouse"]
        cls.company = cls.env.ref("base.main_company")
        cls.warehouse = cls.warehouse_model.create(
            {
                "name": "Test Warehouse",
                "code": "TW",
                "company_id": cls.company.id,
            }
        )

        cls.product1 = cls.product_model.create(
            {
                "name": "Product 1",
                "type": "product",
                "company_id": cls.company.id,
            }
        )
        cls.product2 = cls.product_model.create(
            {
                "name": "Product 2",
                "type": "product",
                "company_id": cls.company.id,
            }
        )
        cls.repair_location = cls.stock_location_model.create(
            {
                "name": "Repair Location",
                "usage": "internal",
                "location_id": cls.warehouse.view_location_id.id,
                "company_id": cls.company.id,
            }
        )
        cls.production_location = cls.stock_location_model.create(
            {
                "name": "Production Location",
                "usage": "production",
                "company_id": cls.company.id,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product1.id,
                "location_id": cls.repair_location.id,
                "quantity": 10,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product2.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 10,
            }
        )

    def test_1step_repair_order_flow(self):
        self.warehouse.write(
            {
                "repair_steps": "1_step",
                "repair_location_id": self.repair_location.id,
            }
        )
        repair_order = self.repair_model.create(
            {
                "product_id": self.product1.id,
                "product_uom": self.product1.uom_id.id,
                "location_id": self.repair_location.id,
                "company_id": self.company.id,
            }
        )
        self.repair_line_model.create(
            {
                "name": "Repair Line 1",
                "repair_id": repair_order.id,
                "product_id": self.product2.id,
                "type": "add",
                "product_uom_qty": 1,
                "product_uom": self.product2.uom_id.id,
                "price_unit": 1,
                "location_id": self.repair_location.id,
                "location_dest_id": self.production_location.id,
            }
        )
        repair_order.action_repair_confirm()
        self.assertEqual(repair_order.state, "confirmed")
        repair_order.action_repair_ready()
        self.assertEqual(repair_order.state, "ready")

    def test_2steps_repair_order_flow(self):
        self.warehouse.write(
            {
                "repair_steps": "2_steps",
                "repair_location_id": self.repair_location.id,
            }
        )
        self.product2.write(
            {"route_ids": [(6, 0, [self.warehouse.repair_route_id.id])]}
        )
        repair_order = self.repair_model.create(
            {
                "product_id": self.product1.id,
                "product_uom": self.product1.uom_id.id,
                "location_id": self.repair_location.id,
                "company_id": self.company.id,
            }
        )
        self.repair_line_model.create(
            {
                "name": "Repair Line 2",
                "repair_id": repair_order.id,
                "product_id": self.product2.id,
                "type": "add",
                "product_uom_qty": 1,
                "product_uom": self.product2.uom_id.id,
                "price_unit": 1,
                "location_id": self.repair_location.id,
                "location_dest_id": self.production_location.id,
            }
        )
        repair_order.action_repair_confirm()
        repair_order._compute_picking_ids()
        self.assertEqual(repair_order.state, "confirmed")
        self.assertTrue(repair_order.picking_ids)
        self.assertEqual(len(repair_order.picking_ids), 1)

    def test_3steps_repair_order_flow(self):
        self.warehouse.write(
            {
                "repair_steps": "3_steps",
                "repair_location_id": self.repair_location.id,
            }
        )
        self.product2.write(
            {"route_ids": [(6, 0, [self.warehouse.repair_route_id.id])]}
        )
        repair_order = self.repair_model.create(
            {
                "product_id": self.product1.id,
                "product_uom": self.product1.uom_id.id,
                "location_id": self.repair_location.id,
                "company_id": self.company.id,
            }
        )
        self.repair_line_model.create(
            {
                "name": "Repair Line 3",
                "repair_id": repair_order.id,
                "product_id": self.product2.id,
                "type": "add",
                "product_uom_qty": 1,
                "product_uom": self.product2.uom_id.id,
                "price_unit": 1,
                "location_id": self.repair_location.id,
                "location_dest_id": self.production_location.id,
            }
        )
        self.repair_line_model.create(
            {
                "name": "Repair Line 4",
                "repair_id": repair_order.id,
                "product_id": self.product2.id,
                "type": "remove",
                "product_uom_qty": 1,
                "product_uom": self.product2.uom_id.id,
                "price_unit": 1,
                "location_id": self.production_location.id,
                "location_dest_id": self.repair_location.id,
            }
        )
        repair_order.action_repair_confirm()
        repair_order._compute_picking_ids()
        self.assertEqual(repair_order.state, "confirmed")
        self.assertTrue(repair_order.picking_ids)
        self.assertEqual(len(repair_order.picking_ids), 2)
        repair_order.action_repair_cancel()
        self.assertEqual(repair_order.state, "cancel")
        for picking in repair_order.picking_ids:
            self.assertEqual(picking.state, "cancel")

    def test_update_related_pickings(self):
        self.warehouse.write(
            {
                "repair_steps": "3_steps",
                "repair_location_id": self.repair_location.id,
            }
        )
        self.product2.write(
            {"route_ids": [(6, 0, [self.warehouse.repair_route_id.id])]}
        )
        repair_order = self.repair_model.create(
            {
                "product_id": self.product1.id,
                "product_uom": self.product1.uom_id.id,
                "location_id": self.repair_location.id,
                "company_id": self.company.id,
            }
        )
        self.repair_line_model.create(
            {
                "name": "Repair Line 3",
                "repair_id": repair_order.id,
                "product_id": self.product2.id,
                "type": "add",
                "product_uom_qty": 1,
                "product_uom": self.product2.uom_id.id,
                "price_unit": 1,
                "location_id": self.repair_location.id,
                "location_dest_id": self.production_location.id,
            }
        )
        repair_order.action_repair_confirm()
        repair_order._compute_picking_ids()
        self.assertEqual(repair_order.state, "confirmed")
        self.assertTrue(repair_order.picking_ids)
        self.assertEqual(len(repair_order.picking_ids), 1)
        self.assertEqual(len(repair_order.picking_ids.move_ids_without_package), 1)
        self.assertEqual(
            repair_order.picking_ids.move_ids_without_package.product_uom_qty, 1
        )
        self.repair_line_model.create(
            {
                "name": "Repair Line Add",
                "repair_id": repair_order.id,
                "product_id": self.product2.id,
                "type": "add",
                "product_uom_qty": 1,
                "product_uom": self.product2.uom_id.id,
                "price_unit": 1,
                "location_id": self.repair_location.id,
                "location_dest_id": self.production_location.id,
            }
        )
        self.assertEqual(len(repair_order.picking_ids), 1)
        self.assertEqual(len(repair_order.picking_ids.move_ids_without_package), 1)
        self.assertEqual(
            repair_order.picking_ids.move_ids_without_package.product_uom_qty, 2
        )
        self.repair_line_model.create(
            {
                "name": "Repair Line Remove",
                "repair_id": repair_order.id,
                "product_id": self.product2.id,
                "type": "remove",
                "product_uom_qty": 1,
                "product_uom": self.product2.uom_id.id,
                "price_unit": 1,
                "location_id": self.production_location.id,
                "location_dest_id": self.repair_location.id,
            }
        )
        repair_order._compute_picking_ids()
        self.assertEqual(len(repair_order.picking_ids), 2)
