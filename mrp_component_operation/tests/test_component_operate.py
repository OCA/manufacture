from odoo import api
from odoo.tests import common


class TestComponentOperation(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestComponentOperation, cls).setUpClass()
        cls.user_admin = cls.env.ref("base.user_admin")
        cls.env = api.Environment(cls.cr, cls.user_admin.id, {})
        cls.ProcurementGroup = cls.env["procurement.group"]
        cls.MrpProduction = cls.env["mrp.production"]
        cls.env.user.company_id.manufacturing_lead = 0
        cls.env.user.tz = False  # Make sure there's no timezone in user

        cls.picking_type = cls.env["stock.picking.type"].search(
            [
                ("code", "=", "mrp_operation"),
                ("sequence_id.company_id", "=", cls.env.user.company_id.id),
            ],
            limit=1,
        )
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "TEST Parent",
                "route_ids": [
                    (6, 0, [cls.env.ref("mrp.route_warehouse0_manufacture").id])
                ],
                "type": "product",
                "produce_delay": 0,
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {"name": "TEST Child", "type": "product"}
        )
        cls.product3 = cls.env["product.product"].create(
            {"name": "TEST Child Serial", "type": "product", "tracking": "serial"}
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_id": cls.product1.id,
                "product_tmpl_id": cls.product1.product_tmpl_id.id,
                "type": "normal",
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.product2.id, "product_qty": 2}),
                    (0, 0, {"product_id": cls.product3.id, "product_qty": 1}),
                ],
            }
        )
        cls.stock_picking_type = cls.env.ref("stock.picking_type_out")
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.user.company_id.id)], limit=1
        )
        cls.warehouse.manufacture_steps = "pbm"
        cls.ressuply_loc1 = cls.warehouse.lot_stock_id
        cls.source_location = cls.env.ref("stock.stock_location_stock")
        cls.destination_location = cls.env.ref("stock.stock_location_output")
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
        cls.source_route = cls.env["stock.location.route"].create(
            {
                "name": "Source Route",
                "mo_component_selectable": True,
                "sequence": 10,
            }
        )

        cls.destination_route = cls.env["stock.location.route"].create(
            {
                "name": "Destination Route",
                "mo_component_selectable": True,
                "sequence": 10,
            }
        )

        cls.env["stock.rule"].create(
            {
                "name": "Transfer",
                "route_id": cls.source_route.id,
                "location_src_id": cls.ressuply_loc1.id,
                "location_id": cls.source_location.id,
                "action": "pull",
                "picking_type_id": cls.warehouse.int_type_id.id,
                "procure_method": "make_to_stock",
                "warehouse_id": cls.warehouse.id,
            }
        )

        cls.env["stock.rule"].create(
            {
                "name": "Transfer 2",
                "route_id": cls.destination_route.id,
                "location_src_id": cls.source_location.id,
                "location_id": cls.destination_location.id,
                "action": "pull",
                "picking_type_id": cls.warehouse.int_type_id.id,
                "procure_method": "make_to_stock",
                "warehouse_id": cls.warehouse.id,
                "propagate_warehouse_id": cls.warehouse.id,
            }
        )

        cls.operation_scrap_replace = cls.env["mrp.component.operation"].create(
            {
                "name": "Operation Scrap and Replace",
                "incoming_operation": "replace",
                "outgoing_operation": "scrap",
                "source_location_id": cls.source_location.id,
                "source_route_id": cls.source_route.id,
                "scrap_location_id": cls.scrapped_location.id,
            }
        )

        cls.operation_no = cls.env["mrp.component.operation"].create(
            {
                "name": "Operation Scrap and Replace",
                "incoming_operation": "no",
                "outgoing_operation": "no",
                "source_location_id": cls.source_location.id,
            }
        )

        cls.operation_move_replace = cls.env["mrp.component.operation"].create(
            {
                "name": "Operation Move",
                "incoming_operation": "replace",
                "outgoing_operation": "move",
                "source_location_id": cls.source_location.id,
                "source_route_id": cls.source_route.id,
                "destination_location_id": cls.destination_location.id,
                "destination_route_id": cls.destination_route.id,
            }
        )

    def test_01_scrap_and_replace(self):
        nb_product_todo = 5
        serials_p2 = []
        for i in range(nb_product_todo):
            serials_p2.append(
                self.env["stock.production.lot"].create(
                    {
                        "name": f"lot_consumed_2_{i}",
                        "product_id": self.product3.id,
                        "company_id": self.env.company.id,
                    }
                )
            )
            self.env["stock.quant"]._update_available_quantity(
                self.product3, self.ressuply_loc1, 1, lot_id=serials_p2[-1]
            )
        self.env["stock.quant"]._update_available_quantity(
            self.product2, self.ressuply_loc1, 10
        )
        mo = self.MrpProduction.create(
            {
                "bom_id": self.bom.id,
                "product_id": self.product1.id,
                "product_qty": 2,
                "product_uom_id": self.product1.uom_id.id,
                "date_deadline": "2023-01-01 15:00:00",
                "date_planned_start": "2023-01-01 15:00:00",
            }
        )
        mo._onchange_move_raw()
        mo._onchange_move_finished()
        mo.action_confirm()
        mo.action_assign()
        self.assertEqual(mo.move_raw_ids[0].move_line_ids.product_uom_qty, 4)
        self.assertEqual(len(mo.move_raw_ids[1].move_line_ids), 2)
        wizard = self.env["mrp.component.operate"].create(
            {
                "product_id": mo.move_raw_ids[1].product_id.id,
                "lot_id": mo.move_raw_ids[1].move_line_ids[0].lot_id.id,
                "operation_id": self.operation_scrap_replace.id,
                "mo_id": mo.id,
            }
        )
        self.assertEqual(wizard.product_qty, 1)
        self.assertEqual(wizard.product_id, self.product3)
        lot = wizard.lot_id
        wizard.action_operate_component()
        self.assertEqual(len(mo.picking_ids), 1)
        self.assertEqual(mo.scrap_ids.product_id, self.product3)
        self.assertEqual(mo.scrap_ids.lot_id, lot)
        self.assertEqual(mo.scrap_ids.state, "done")
        self.assertEqual(len(mo.move_raw_ids[1].move_line_ids), 1)
        self.assertEqual(len(mo.move_raw_ids[1].move_orig_ids.move_line_ids), 0)
        self.assertEqual(mo.picking_ids.product_id, self.product3)
        mo.picking_ids.action_assign()
        mo.picking_ids.button_validate()
        self.assertEqual(len(mo.move_raw_ids[1].move_line_ids), 1)
        self.assertEqual(len(mo.move_raw_ids[1].move_orig_ids.move_line_ids), 1)

    def test_02_move_and_replace(self):
        nb_product_todo = 5
        serials_p2 = []
        for i in range(nb_product_todo):
            serials_p2.append(
                self.env["stock.production.lot"].create(
                    {
                        "name": f"lot_consumed_2_{i}",
                        "product_id": self.product3.id,
                        "company_id": self.env.company.id,
                    }
                )
            )
            self.env["stock.quant"]._update_available_quantity(
                self.product3, self.ressuply_loc1, 1, lot_id=serials_p2[-1]
            )
        self.env["stock.quant"]._update_available_quantity(
            self.product2, self.ressuply_loc1, 10
        )
        mo = self.MrpProduction.create(
            {
                "bom_id": self.bom.id,
                "product_id": self.product1.id,
                "product_qty": 1,
                "product_uom_id": self.product1.uom_id.id,
                "date_deadline": "2023-01-01 15:00:00",
                "date_planned_start": "2023-01-01 15:00:00",
            }
        )
        mo._onchange_move_raw()
        mo._onchange_move_finished()
        mo.action_confirm()
        mo.action_assign()
        self.assertEqual(mo.move_raw_ids[0].move_line_ids.product_uom_qty, 2)
        self.assertEqual(len(mo.move_raw_ids[1].move_line_ids), 1)
        wizard = self.env["mrp.component.operate"].create(
            {
                "product_id": mo.move_raw_ids[1].product_id.id,
                "lot_id": mo.move_raw_ids[1].move_line_ids[0].lot_id.id,
                "operation_id": self.operation_move_replace.id,
                "mo_id": mo.id,
            }
        )
        self.assertEqual(wizard.product_qty, 1)
        self.assertEqual(wizard.product_id, self.product3)
        lot = wizard.lot_id
        wizard.action_operate_component()
        self.assertEqual(len(mo.picking_ids), 2)
        self.assertEqual(mo.picking_ids[1].location_dest_id, self.destination_location)
        self.assertEqual(mo.picking_ids[1].move_lines.product_id, self.product3)
        self.assertEqual(mo.picking_ids[0].location_dest_id, self.source_location)
        self.assertEqual(mo.picking_ids[0].move_lines.product_id, self.product3)
        self.assertEqual(len(mo.move_raw_ids[1].move_line_ids), 0)
        self.assertEqual(len(mo.move_raw_ids[1].move_orig_ids.move_line_ids), 0)
        mo.picking_ids[1].action_assign()
        mo.picking_ids[1].button_validate()
        self.assertEqual(
            mo.picking_ids[1].move_line_ids.location_dest_id, self.destination_location
        )
        self.assertEqual(mo.picking_ids[1].move_line_ids.lot_id, lot)
        self.assertEqual(len(mo.move_raw_ids[1].move_line_ids), 0)
        self.assertEqual(len(mo.move_raw_ids[1].move_orig_ids.move_line_ids), 0)
        mo.picking_ids[0].action_assign()
        mo.picking_ids[0].button_validate()
        self.assertEqual(
            mo.picking_ids[0].move_line_ids.location_dest_id, self.source_location
        )
        self.assertEqual(mo.picking_ids[0].move_line_ids.product_id, self.product3)
        self.assertEqual(len(mo.move_raw_ids[1].move_line_ids), 0)
        self.assertEqual(len(mo.move_raw_ids[1].move_orig_ids.move_line_ids), 1)

    def test_03_nothing_and_nothing(self):
        nb_product_todo = 5
        serials_p2 = []
        for i in range(nb_product_todo):
            serials_p2.append(
                self.env["stock.production.lot"].create(
                    {
                        "name": f"lot_consumed_2_{i}",
                        "product_id": self.product3.id,
                        "company_id": self.env.company.id,
                    }
                )
            )
            self.env["stock.quant"]._update_available_quantity(
                self.product3, self.ressuply_loc1, 1, lot_id=serials_p2[-1]
            )
        self.env["stock.quant"]._update_available_quantity(
            self.product2, self.ressuply_loc1, 10
        )
        mo = self.MrpProduction.create(
            {
                "bom_id": self.bom.id,
                "product_id": self.product1.id,
                "product_qty": 2,
                "product_uom_id": self.product1.uom_id.id,
                "date_deadline": "2023-01-01 15:00:00",
                "date_planned_start": "2023-01-01 15:00:00",
            }
        )
        mo._onchange_move_raw()
        mo._onchange_move_finished()
        mo.action_confirm()
        mo.action_assign()
        self.assertEqual(mo.move_raw_ids[0].move_line_ids.product_uom_qty, 4)
        self.assertEqual(len(mo.move_raw_ids[1].move_line_ids), 2)
        wizard = self.env["mrp.component.operate"].create(
            {
                "product_id": mo.move_raw_ids[1].product_id.id,
                "lot_id": mo.move_raw_ids[1].move_line_ids[0].lot_id.id,
                "operation_id": self.operation_no.id,
                "mo_id": mo.id,
            }
        )
        self.assertEqual(wizard.product_qty, 1)
        self.assertEqual(wizard.product_id, self.product3)
        wizard.action_operate_component()
        self.assertEqual(len(mo.picking_ids), 0)
        self.assertEqual(mo.move_raw_ids[0].move_line_ids.product_uom_qty, 4)
        self.assertEqual(len(mo.move_raw_ids[1].move_line_ids), 2)
