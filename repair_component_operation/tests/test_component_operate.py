# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields
from odoo.tests import common


class TestComponentOperation(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestComponentOperation, cls).setUpClass()
        cls.user_admin = cls.env.ref("base.user_admin")
        cls.env = api.Environment(cls.cr, cls.user_admin.id, {})
        cls.ProcurementGroup = cls.env["procurement.group"]
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
                "type": "product",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {"name": "TEST Child", "type": "product"}
        )
        cls.product3 = cls.env["product.product"].create(
            {"name": "TEST Child Serial", "type": "product", "tracking": "serial"}
        )
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.user.company_id.id)], limit=1
        )
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
                "repair_component_selectable": True,
                "sequence": 10,
            }
        )

        cls.destination_route = cls.env["stock.location.route"].create(
            {
                "name": "Destination Route",
                "repair_component_selectable": True,
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

        cls.operation_scrap_replace = cls.env["repair.component.operation"].create(
            {
                "name": "Operation Scrap and Replace",
                "incoming_operation": "replace",
                "outgoing_operation": "scrap",
                "source_location_id": cls.source_location.id,
                "source_route_id": cls.source_route.id,
                "scrap_location_id": cls.scrapped_location.id,
            }
        )

        cls.operation_no = cls.env["repair.component.operation"].create(
            {
                "name": "Operation Scrap and Replace",
                "incoming_operation": "no",
                "outgoing_operation": "no",
                "source_location_id": cls.source_location.id,
            }
        )

        cls.operation_move_replace = cls.env["repair.component.operation"].create(
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

        cls.env["stock.quant"]._update_available_quantity(
            cls.product1, cls.ressuply_loc1, 10
        )

    @classmethod
    def _do_picking(cls, picking):
        picking.action_assign()
        date = fields.Datetime.now()
        picking.action_confirm()
        picking.move_lines.quantity_done = picking.move_lines.product_uom_qty
        picking._action_done()
        for move in picking.move_lines:
            move.date = date

    def test_01_scrap_and_replace(self):
        nb_product_todo = 5
        serials_p3 = []
        for i in range(nb_product_todo):
            serials_p3.append(
                self.env["stock.production.lot"].create(
                    {
                        "name": f"lot_consumed_2_{i}",
                        "product_id": self.product3.id,
                        "company_id": self.env.company.id,
                    }
                )
            )
            self.env["stock.quant"]._update_available_quantity(
                self.product3, self.ressuply_loc1, 1, lot_id=serials_p3[-1]
            )
        repair = self.env["repair.order"].create(
            {
                "product_id": self.product1.id,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "location_id": self.source_location.id,
                "operations": [
                    (
                        0,
                        0,
                        {
                            "location_dest_id": self.ressuply_loc1.id,
                            "location_id": self.source_location.id,
                            "name": self.product1.display_name,
                            "product_id": self.product3.id,
                            "product_uom": self.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 1.0,
                            "lot_id": serials_p3[0].id,
                            "price_unit": 50.0,
                            "type": "add",
                            "company_id": self.env.company.id,
                        },
                    )
                ],
            }
        )
        repair.action_validate()
        repair.action_assign()
        raw_move_product_3 = repair.operations.move_id.filtered(
            lambda m: m.product_id == self.product3
        )
        self.assertEqual(len(raw_move_product_3.move_line_ids), 1)
        lot = raw_move_product_3.move_line_ids[0].lot_id
        wizard = self.env["repair.component.operate"].create(
            {
                "product_id": self.product3.id,
                "lot_id": lot.id,
                "operation_id": self.operation_scrap_replace.id,
                "repair_id": repair.id,
            }
        )
        self.assertEqual(wizard.product_qty, 1)
        wizard.action_operate_component()
        self.assertEqual(len(repair.picking_ids), 1)
        self.assertEqual(repair.scrap_ids.product_id, self.product3)
        self.assertEqual(repair.scrap_ids.lot_id, lot)
        self.assertEqual(repair.scrap_ids.state, "done")
        self.assertEqual(len(raw_move_product_3.move_line_ids), 0)
        self.assertEqual(len(raw_move_product_3.move_orig_ids.move_line_ids), 0)
        self.assertEqual(repair.picking_ids.product_id, self.product3)
        self._do_picking(repair.picking_ids)
        self.assertEqual(repair.picking_ids.state, "done")
        self.assertEqual(
            len(raw_move_product_3.move_line_ids),
            1,
            "The reservation should have been propagated to repair.",
        )
        self.assertEqual(len(raw_move_product_3.move_orig_ids.move_line_ids), 1)

    def test_02_move_and_replace(self):
        nb_product_todo = 5
        serials_p3 = []
        for i in range(nb_product_todo):
            serials_p3.append(
                self.env["stock.production.lot"].create(
                    {
                        "name": f"lot_consumed_2_{i}",
                        "product_id": self.product3.id,
                        "company_id": self.env.company.id,
                    }
                )
            )
            self.env["stock.quant"]._update_available_quantity(
                self.product3, self.ressuply_loc1, 1, lot_id=serials_p3[-1]
            )
        repair = self.env["repair.order"].create(
            {
                "product_id": self.product1.id,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "location_id": self.source_location.id,
                "operations": [
                    (
                        0,
                        0,
                        {
                            "location_dest_id": self.ressuply_loc1.id,
                            "location_id": self.source_location.id,
                            "name": self.product1.display_name,
                            "product_id": self.product3.id,
                            "product_uom": self.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 1.0,
                            "lot_id": serials_p3[0].id,
                            "price_unit": 50.0,
                            "type": "add",
                            "company_id": self.env.company.id,
                        },
                    )
                ],
            }
        )
        repair.action_validate()
        repair.action_assign()
        raw_move_product_3 = repair.operations.move_id.filtered(
            lambda m: m.product_id == self.product3
        )
        self.assertEqual(len(raw_move_product_3.move_line_ids), 1)
        lot = raw_move_product_3.move_line_ids[0].lot_id
        wizard = self.env["repair.component.operate"].create(
            {
                "product_id": self.product3.id,
                "lot_id": lot.id,
                "operation_id": self.operation_move_replace.id,
                "repair_id": repair.id,
            }
        )
        self.assertEqual(wizard.product_qty, 1)
        self.assertEqual(len(repair.picking_ids), 0)
        wizard.action_operate_component()
        self.assertEqual(len(repair.picking_ids), 2)
        moves_for_replacement = repair.mapped("picking_ids.move_lines")
        self.assertEqual(len(moves_for_replacement), 2)
        for move in moves_for_replacement:
            self.assertEqual(
                move.product_id,
                self.product3,
            )
        replacement_first_move = moves_for_replacement.filtered(
            lambda m: m.location_dest_id == self.destination_location
        )
        self.assertTrue(replacement_first_move)
        replacement_second_move = moves_for_replacement.filtered(
            lambda m: m.location_dest_id == self.source_location
        )
        self.assertTrue(replacement_second_move)
        self.assertEqual(
            len(raw_move_product_3.move_line_ids),
            0,
            "Reservation for product3 should have been cleared",
        )
        self.assertEqual(raw_move_product_3.move_orig_ids, replacement_second_move)
        self.assertEqual(len(replacement_second_move.move_line_ids), 0)
        self._do_picking(replacement_first_move.picking_id)
        self.assertEqual(replacement_first_move.state, "done")
        self.assertEqual(replacement_first_move.move_line_ids.lot_id, lot)
        self.assertEqual(
            len(raw_move_product_3.move_line_ids),
            0,
            "raw move for product 3 still not reserved.",
        )
        self.assertEqual(len(replacement_second_move.move_line_ids), 0)
        self._do_picking(replacement_second_move.picking_id)
        self.assertEqual(replacement_second_move.state, "done")
        self.assertEqual(replacement_first_move.product_id, self.product3)
        repair.action_assign()
        self.assertEqual(len(raw_move_product_3.move_line_ids), 1)

    def test_03_nothing_and_nothing(self):
        nb_product_todo = 5
        serials_p3 = []
        for i in range(nb_product_todo):
            serials_p3.append(
                self.env["stock.production.lot"].create(
                    {
                        "name": f"lot_consumed_2_{i}",
                        "product_id": self.product3.id,
                        "company_id": self.env.company.id,
                    }
                )
            )
            self.env["stock.quant"]._update_available_quantity(
                self.product3, self.ressuply_loc1, 1, lot_id=serials_p3[-1]
            )
        repair = self.env["repair.order"].create(
            {
                "product_id": self.product1.id,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "location_id": self.source_location.id,
                "operations": [
                    (
                        0,
                        0,
                        {
                            "location_dest_id": self.ressuply_loc1.id,
                            "location_id": self.source_location.id,
                            "name": self.product1.display_name,
                            "product_id": self.product3.id,
                            "product_uom": self.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 1.0,
                            "lot_id": serials_p3[0].id,
                            "price_unit": 50.0,
                            "type": "add",
                            "company_id": self.env.company.id,
                        },
                    )
                ],
            }
        )
        repair.action_validate()
        repair.action_assign()
        raw_move_product_3 = repair.operations.move_id.filtered(
            lambda m: m.product_id == self.product3
        )
        self.assertEqual(len(raw_move_product_3.move_line_ids), 1)
        wizard = self.env["repair.component.operate"].create(
            {
                "product_id": self.product3.id,
                "lot_id": raw_move_product_3.move_line_ids[0].lot_id.id,
                "operation_id": self.operation_no.id,
                "repair_id": repair.id,
            }
        )
        self.assertEqual(wizard.product_qty, 1)
        self.assertEqual(wizard.product_id, self.product3)
        wizard.action_operate_component()
        self.assertEqual(len(repair.picking_ids), 0)
        self.assertEqual(raw_move_product_3.move_line_ids.product_uom_qty, 1)
        self.assertEqual(len(raw_move_product_3.move_line_ids), 1)
