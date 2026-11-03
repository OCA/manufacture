# Copyright 2026 Melvin Diabat @ OpenITech
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestManufactureThenStore(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids += cls.env.ref("stock.group_adv_location")
        cls.warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "Manufacture Then Store Test",
                "code": "MTS",
                "manufacture_steps": "ms",
            }
        )
        cls.finished_product, cls.component = cls.env["product.product"].create(
            [
                {"name": "Test finished product", "is_storable": True},
                {"name": "Test component", "is_storable": True},
            ]
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_id": cls.finished_product.id,
                "product_tmpl_id": cls.finished_product.product_tmpl_id.id,
                "product_qty": 1,
                "product_uom_id": cls.finished_product.uom_id.id,
                "consumption": "flexible",
                "bom_line_ids": [
                    Command.create({"product_id": cls.component.id, "product_qty": 2})
                ],
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.component, cls.warehouse.lot_stock_id, 20
        )

    def _create_mo(self, warehouse=None, qty=2, confirm=True):
        warehouse = warehouse or self.warehouse
        production_form = Form(self.env["mrp.production"])
        production_form.picking_type_id = warehouse.manu_type_id
        production_form.product_id = self.finished_product
        production_form.bom_id = self.bom
        production_form.product_qty = qty
        production = production_form.save()
        if confirm:
            production.action_confirm()
        return production

    def _store_move(self, production):
        return production.move_finished_ids.filtered(
            lambda move: move.product_id == production.product_id
        ).move_dest_ids.filtered(
            lambda move: move.picking_type_id == production.warehouse_id.sam_type_id
        )

    def _quantity(self, location):
        return sum(
            self.env["stock.quant"]
            ._gather(self.finished_product, location)
            .mapped("quantity")
        )

    def _warehouse_configuration(self, warehouse):
        return (
            warehouse.manufacture_steps,
            warehouse.pbm_loc_id.active,
            warehouse.sam_loc_id.active,
            warehouse.pbm_type_id.active,
            warehouse.sam_type_id.active,
            warehouse.manu_type_id.default_location_src_id.id,
            warehouse.manu_type_id.default_location_dest_id.id,
            warehouse.pbm_route_id.active,
            tuple(warehouse.pbm_route_id.rule_ids.ids),
        )

    def _create_pending_move(self, source, destination):
        move = self.env["stock.move"].create(
            {
                "product_id": self.finished_product.id,
                "product_uom": self.finished_product.uom_id.id,
                "product_uom_qty": 1,
                "location_id": source.id,
                "location_dest_id": destination.id,
            }
        )
        move._action_confirm()
        return move

    def test_warehouse_configuration(self):
        warehouse = self.warehouse
        self.assertEqual(warehouse.manufacture_steps, "ms")
        self.assertTrue(warehouse.sam_loc_id.active)
        self.assertFalse(warehouse.pbm_loc_id.active)
        self.assertTrue(warehouse.sam_type_id.active)
        self.assertFalse(warehouse.pbm_type_id.active)
        self.assertEqual(
            warehouse.manu_type_id.default_location_src_id, warehouse.lot_stock_id
        )
        self.assertEqual(
            warehouse.manu_type_id.default_location_dest_id, warehouse.sam_loc_id
        )
        self.assertEqual(len(warehouse.pbm_route_id.rule_ids), 1)
        self.assertEqual(warehouse.pbm_route_id.rule_ids.action, "push")
        self.assertFalse(warehouse.pbm_mto_pull_id.active)
        rule_ids = warehouse.pbm_route_id.rule_ids.ids
        warehouse.write({"manufacture_steps": "ms"})
        self.assertEqual(warehouse.pbm_route_id.rule_ids.ids, rule_ids)
        warehouse.manufacture_steps = "mrp_one_step"
        self.assertFalse(warehouse.sam_loc_id.active)
        warehouse.manufacture_steps = "ms"
        self.assertEqual(warehouse.pbm_route_id.rule_ids.ids, rule_ids)
        self.assertTrue(warehouse.sam_loc_id.active)

    def test_switch_from_three_steps_reuses_stocked_post_production(self):
        warehouse = self.env["stock.warehouse"].create(
            {
                "name": "Stocked Three Step Test",
                "code": "STS",
                "manufacture_steps": "pbm_sam",
            }
        )
        post_production = warehouse.sam_loc_id
        pre_production = warehouse.pbm_loc_id
        self.env["stock.quant"]._update_available_quantity(
            self.finished_product, post_production, 1
        )
        self.env["stock.quant"]._update_available_quantity(
            self.component, pre_production, 1
        )

        warehouse.manufacture_steps = "ms"

        self.assertEqual(warehouse.sam_loc_id, post_production)
        self.assertTrue(post_production.active)
        self.assertTrue(pre_production.active)
        self.assertEqual(
            warehouse.manu_type_id.default_location_dest_id, post_production
        )
        self.assertEqual(warehouse.sam_type_id.default_location_src_id, post_production)
        self.assertEqual(len(warehouse.pbm_route_id.rule_ids), 1)
        self.assertEqual(warehouse.pbm_route_id.rule_ids.action, "push")
        self.assertFalse(warehouse.pbm_type_id.active)

    def test_enable_ms_on_existing_three_step_warehouse(self):
        warehouse = self.env["stock.warehouse"].create(
            {
                "name": "Existing Three Step Warehouse",
                "code": "ETW",
                "manufacture_steps": "pbm_sam",
            }
        )
        pre_production = warehouse.pbm_loc_id
        post_production = warehouse.sam_loc_id
        self.env["stock.quant"]._update_available_quantity(
            self.component, warehouse.lot_stock_id, 2
        )

        warehouse.manufacture_steps = "ms"
        production = self._create_mo(warehouse, qty=1)

        self.assertEqual(warehouse.pbm_loc_id, pre_production)
        self.assertEqual(warehouse.sam_loc_id, post_production)
        self.assertEqual(production.move_raw_ids.location_id, warehouse.lot_stock_id)
        self.assertFalse(production.move_raw_ids.move_orig_ids)
        self.assertFalse(production.picking_ids)
        production.action_assign()
        production.qty_producing = 1
        production.button_mark_done()

        storage_move = self._store_move(production)
        self.assertEqual(len(storage_move), 1)
        self.assertEqual(storage_move.location_id, post_production)
        self.assertEqual(storage_move.location_dest_id, warehouse.lot_stock_id)
        self.assertEqual(storage_move.picking_type_id, warehouse.sam_type_id)
        self.assertEqual(storage_move.state, "assigned")

    def test_empty_location_transitions_follow_standard_modes(self):
        warehouse = self.warehouse
        for step, pre_active, post_active in (
            ("mrp_one_step", False, False),
            ("ms", False, True),
            ("pbm", True, False),
            ("ms", True, True),
            ("pbm_sam", True, True),
            ("ms", True, True),
        ):
            with self.subTest(step=step):
                warehouse.manufacture_steps = step
                self.assertEqual(warehouse.pbm_loc_id.active, pre_active)
                self.assertEqual(warehouse.sam_loc_id.active, post_active)

    def test_stocked_post_production_blocks_archiving(self):
        warehouse = self.warehouse
        self.env["stock.quant"]._update_available_quantity(
            self.finished_product, warehouse.sam_loc_id, 1
        )
        configuration = self._warehouse_configuration(warehouse)
        for step in ("mrp_one_step", "pbm"):
            with self.subTest(step=step), self.assertRaises(UserError):
                warehouse.manufacture_steps = step
            self.assertEqual(self._warehouse_configuration(warehouse), configuration)

        warehouse.manufacture_steps = "pbm_sam"
        self.assertTrue(warehouse.sam_loc_id.active)
        self.assertEqual(self._quantity(warehouse.sam_loc_id), 1)

    def test_stocked_pre_production_blocks_only_its_archiving(self):
        warehouse = self.env["stock.warehouse"].create(
            {
                "name": "Stocked Pre-Production Test",
                "code": "SPT",
                "manufacture_steps": "pbm_sam",
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            self.component, warehouse.pbm_loc_id, 1
        )
        warehouse.manufacture_steps = "ms"
        configuration = self._warehouse_configuration(warehouse)
        with self.assertRaises(UserError):
            warehouse.manufacture_steps = "mrp_one_step"
        self.assertEqual(self._warehouse_configuration(warehouse), configuration)

        warehouse.manufacture_steps = "pbm"
        self.assertTrue(warehouse.pbm_loc_id.active)
        self.assertFalse(warehouse.sam_loc_id.active)

    def test_pending_post_production_transfer_blocks_archiving(self):
        warehouse = self.warehouse
        move = self._create_pending_move(warehouse.sam_loc_id, warehouse.lot_stock_id)
        self.assertEqual(move.state, "confirmed")
        configuration = self._warehouse_configuration(warehouse)
        for step in ("mrp_one_step", "pbm"):
            with (
                self.subTest(step=step),
                self.assertRaisesRegex(UserError, "Finish or cancel stock operations"),
            ):
                warehouse.manufacture_steps = step
            self.assertEqual(self._warehouse_configuration(warehouse), configuration)

        warehouse.manufacture_steps = "pbm_sam"
        self.assertEqual(move.state, "confirmed")
        warehouse.manufacture_steps = "ms"
        move._action_cancel()
        warehouse.manufacture_steps = "pbm"
        self.assertFalse(warehouse.sam_loc_id.active)

    def test_unrelated_warehouse_transfer_does_not_block_transition(self):
        warehouse = self.warehouse
        other = self.env["stock.warehouse"].create(
            {
                "name": "Unrelated Three Step Warehouse",
                "code": "UTW",
                "manufacture_steps": "pbm_sam",
            }
        )
        move = self._create_pending_move(other.sam_loc_id, other.lot_stock_id)

        warehouse.manufacture_steps = "pbm"
        self.assertFalse(warehouse.sam_loc_id.active)
        warehouse.manufacture_steps = "ms"
        warehouse.manufacture_steps = "mrp_one_step"

        self.assertFalse(warehouse.sam_loc_id.active)
        self.assertTrue(other.sam_loc_id.active)
        self.assertEqual(move.state, "confirmed")

    def test_only_active_descendants_block_archiving(self):
        warehouse = self.warehouse
        sublocation = self.env["stock.location"].create(
            {
                "name": "Post-Production Shelf",
                "usage": "internal",
                "location_id": warehouse.sam_loc_id.id,
                "company_id": warehouse.company_id.id,
            }
        )
        move = self._create_pending_move(sublocation, warehouse.lot_stock_id)
        with self.assertRaisesRegex(UserError, "Finish or cancel stock operations"):
            warehouse.manufacture_steps = "pbm"

        sublocation.active = False
        warehouse.manufacture_steps = "pbm"
        self.assertFalse(warehouse.sam_loc_id.active)
        self.assertEqual(move.state, "confirmed")

    def test_pending_pre_production_blocks_one_step(self):
        warehouse = self.env["stock.warehouse"].create(
            {
                "name": "Pending Pre-Production Test",
                "code": "PPT",
                "manufacture_steps": "pbm_sam",
            }
        )
        move = self._create_pending_move(warehouse.lot_stock_id, warehouse.pbm_loc_id)
        warehouse.manufacture_steps = "ms"
        configuration = self._warehouse_configuration(warehouse)
        with self.assertRaisesRegex(UserError, "Finish or cancel stock operations"):
            warehouse.manufacture_steps = "mrp_one_step"
        self.assertEqual(self._warehouse_configuration(warehouse), configuration)

        warehouse.manufacture_steps = "pbm"
        self.assertTrue(warehouse.pbm_loc_id.active)
        move._action_cancel()

    def test_pending_move_line_blocks_post_production_archiving(self):
        warehouse = self.warehouse
        destination = self.env.ref("stock.stock_location_customers")
        move = self._create_pending_move(warehouse.lot_stock_id, destination)
        move_line = self.env["stock.move.line"].create(
            {
                "move_id": move.id,
                "product_id": self.finished_product.id,
                "product_uom_id": self.finished_product.uom_id.id,
                "location_id": warehouse.sam_loc_id.id,
                "location_dest_id": destination.id,
            }
        )
        self.assertEqual(move_line.location_id, warehouse.sam_loc_id)
        configuration = self._warehouse_configuration(warehouse)
        with self.assertRaisesRegex(UserError, "Finish or cancel stock operations"):
            warehouse.manufacture_steps = "mrp_one_step"
        self.assertEqual(self._warehouse_configuration(warehouse), configuration)

    def test_batch_transition_rolls_back_on_stocked_location(self):
        warehouse = self.warehouse
        other = self.env["stock.warehouse"].create(
            {
                "name": "Second Manufacture Then Store Test",
                "code": "SMT",
                "manufacture_steps": "ms",
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            self.finished_product, other.sam_loc_id, 1
        )
        configurations = {
            record.id: self._warehouse_configuration(record)
            for record in warehouse | other
        }
        with self.assertRaises(UserError):
            (warehouse | other).write({"manufacture_steps": "pbm"})
        for record in warehouse | other:
            self.assertEqual(
                self._warehouse_configuration(record), configurations[record.id]
            )

    def test_confirmed_mo_blocks_post_production_archiving(self):
        warehouse = self.warehouse
        production = self._create_mo()
        configuration = self._warehouse_configuration(warehouse)
        with self.assertRaisesRegex(UserError, "Finish or cancel stock operations"):
            warehouse.manufacture_steps = "pbm"
        self.assertEqual(self._warehouse_configuration(warehouse), configuration)
        self.assertEqual(production.state, "confirmed")

    def test_confirmation_does_not_create_storage_transfer(self):
        production = self._create_mo()
        self.assertEqual(
            production.move_raw_ids.location_id, self.warehouse.lot_stock_id
        )
        self.assertFalse(production.move_raw_ids.move_orig_ids)
        self.assertEqual(production.move_raw_ids.raw_material_production_id, production)
        self.assertEqual(
            production.move_finished_ids.location_dest_id, self.warehouse.sam_loc_id
        )
        self.assertFalse(self._store_move(production))
        self.assertFalse(production.picking_ids)
        production.action_confirm()
        self.assertFalse(self._store_move(production))

    def test_finished_goods_require_separate_transfer(self):
        production = self._create_mo()
        production.action_assign()
        production.qty_producing = production.product_qty
        production.button_mark_done()
        storage_move = self._store_move(production)
        self.assertEqual(production.state, "done")
        self.assertEqual(len(storage_move), 1)
        self.assertEqual(storage_move.location_id, self.warehouse.sam_loc_id)
        self.assertEqual(storage_move.location_dest_id, self.warehouse.lot_stock_id)
        self.assertEqual(storage_move.move_orig_ids, production.move_finished_ids)
        self.assertEqual(storage_move.state, "assigned")
        self.assertEqual(storage_move.picking_id.state, "assigned")
        self.assertEqual(len(production.move_finished_ids.move_dest_ids), 1)
        self.assertEqual(self._quantity(self.warehouse.sam_loc_id), 2)
        self.assertEqual(self._quantity(self.warehouse.lot_stock_id), 0)

    def test_no_duplicate_storage_after_completion(self):
        production = self._create_mo()
        production.action_assign()
        production.qty_producing = production.product_qty
        production.button_mark_done()
        storage_move = self._store_move(production)
        storage_picking = storage_move.picking_id
        storage_moves = self.env["stock.move"].search(
            [
                ("production_group_id", "=", production.production_group_id.id),
                ("picking_type_id", "=", self.warehouse.sam_type_id.id),
            ]
        )
        self.assertEqual(storage_moves, storage_move)
        self.assertEqual(storage_moves.picking_id, storage_picking)
        self.assertEqual(production.picking_ids, storage_picking)

    def test_byproducts_use_same_storage_transfer(self):
        self.env.user.group_ids += self.env.ref("mrp.group_mrp_byproducts")
        byproduct = self.env["product.product"].create(
            {"name": "Test byproduct", "is_storable": True}
        )
        self.bom.byproduct_ids = [
            Command.create({"product_id": byproduct.id, "product_qty": 1})
        ]
        production = self._create_mo()
        self.assertFalse(production.move_finished_ids.move_dest_ids)
        production.action_assign()
        production.qty_producing = production.product_qty
        production.button_mark_done()
        storage_moves = production.move_finished_ids.move_dest_ids.filtered(
            lambda move: move.picking_type_id == self.warehouse.sam_type_id
        )
        self.assertEqual(
            set(storage_moves.product_id.ids), {self.finished_product.id, byproduct.id}
        )
        self.assertEqual(len(storage_moves), 2)
        self.assertEqual(len(storage_moves.picking_id), 1)
        self.assertEqual(set(storage_moves.mapped("state")), {"assigned"})
        self.assertEqual(len(production.picking_ids), 1)

    def test_simultaneous_confirmation_and_independent_cancellation(self):
        first = self._create_mo(confirm=False)
        second = self._create_mo(confirm=False)
        (first | second).action_confirm()
        self.assertFalse(self._store_move(first))
        self.assertFalse(self._store_move(second))
        first.action_cancel()
        self.assertFalse(first.picking_ids)
        second.action_assign()
        second.qty_producing = second.product_qty
        second.button_mark_done()
        second_storage = self._store_move(second)
        self.assertEqual(len(second_storage), 1)
        self.assertEqual(second_storage.state, "assigned")
        self.assertFalse(self._store_move(first))
        self.assertEqual(len(self._store_move(second)), 1)

    def test_transfer_validation(self):
        production = self._create_mo()
        production.action_assign()
        production.qty_producing = production.product_qty
        production.button_mark_done()
        storage_move = self._store_move(production)
        storage_move.picked = True
        storage_move.picking_id.button_validate()
        self.assertEqual(storage_move.state, "done")
        self.assertEqual(self._quantity(self.warehouse.sam_loc_id), 0)
        self.assertEqual(self._quantity(self.warehouse.lot_stock_id), 2)

    def test_partial_production_backorder(self):
        production = self._create_mo(qty=3)
        self.assertFalse(self._store_move(production))
        production.action_assign()
        production_form = Form(production)
        production_form.qty_producing = 1
        production = production_form.save()
        action = production.button_mark_done()
        Form(
            self.env["mrp.production.backorder"].with_context(**action["context"])
        ).save().action_backorder()
        storage_move = self._store_move(production)
        self.assertEqual(production.state, "done")
        self.assertEqual(storage_move.product_uom_qty, 1)
        self.assertEqual(storage_move.quantity, 1)
        self.assertEqual(storage_move.state, "assigned")
        self.assertEqual(self._quantity(self.warehouse.sam_loc_id), 1)
        backorder = production.production_group_id.production_ids - production
        self.assertEqual(len(backorder), 1)
        self.assertFalse(self._store_move(backorder))
        backorder.action_assign()
        backorder.qty_producing = backorder.product_qty
        backorder.button_mark_done()
        storage_moves = storage_move | self._store_move(backorder)
        self.assertEqual(sum(storage_moves.mapped("product_uom_qty")), 3)
        self.assertEqual(sum(storage_moves.mapped("quantity")), 3)
        self.assertEqual(set(storage_moves.mapped("state")), {"assigned"})

    def test_store_partial_production_before_manufacturing_backorder(self):
        production = self._create_mo(qty=3)
        production.action_assign()
        production_form = Form(production)
        production_form.qty_producing = 1
        production = production_form.save()
        action = production.button_mark_done()
        Form(
            self.env["mrp.production.backorder"].with_context(**action["context"])
        ).save().action_backorder()

        storage_move = self._store_move(production)
        storage_move.picked = True
        action = storage_move.picking_id.button_validate()
        self.assertNotIsInstance(action, dict)
        self.assertEqual(storage_move.state, "done")
        self.assertEqual(self._quantity(self.warehouse.lot_stock_id), 1)

        backorder = production.production_group_id.production_ids - production
        backorder.action_assign()
        backorder.qty_producing = backorder.product_qty
        backorder.button_mark_done()
        storage_moves = self.env["stock.move"].search(
            [
                ("production_group_id", "=", production.production_group_id.id),
                ("picking_type_id", "=", self.warehouse.sam_type_id.id),
            ]
        )
        self.assertEqual(len(storage_moves), 2)
        self.assertEqual(sum(storage_moves.mapped("product_uom_qty")), 3)
        remaining_storage_move = storage_moves - storage_move
        self.assertEqual(remaining_storage_move.state, "assigned")
        self.assertEqual(remaining_storage_move.quantity, 2)
        remaining_storage_move.picked = True
        remaining_storage_move.picking_id.button_validate()
        self.assertEqual(self._quantity(self.warehouse.lot_stock_id), 3)
        self.assertEqual(self._quantity(self.warehouse.sam_loc_id), 0)

    def test_cancel_manufacturing_backorder_keeps_produced_storage(self):
        production = self._create_mo(qty=3)
        production.action_assign()
        production_form = Form(production)
        production_form.qty_producing = 1
        production = production_form.save()
        action = production.button_mark_done()
        Form(
            self.env["mrp.production.backorder"].with_context(**action["context"])
        ).save().action_backorder()
        storage_move = self._store_move(production)
        backorder = production.production_group_id.production_ids - production

        backorder.action_cancel()

        self.assertEqual(storage_move.product_uom_qty, 1)
        self.assertEqual(storage_move.quantity, 1)
        self.assertEqual(storage_move.state, "assigned")
        storage_move.picked = True
        storage_move.picking_id.button_validate()
        self.assertEqual(self._quantity(self.warehouse.lot_stock_id), 1)
        self.assertEqual(self._quantity(self.warehouse.sam_loc_id), 0)

    def test_lot_tracked_finished_goods(self):
        self.finished_product.tracking = "lot"
        production = self._create_mo()
        production.action_assign()
        production.action_generate_serial()
        production.qty_producing = production.product_qty
        production.button_mark_done()
        storage_move = self._store_move(production)
        self.assertEqual(storage_move.state, "assigned")
        self.assertEqual(
            storage_move.move_line_ids.lot_id, production.lot_producing_ids
        )
        storage_move.picked = True
        storage_move.picking_id.button_validate()
        self.assertEqual(storage_move.state, "done")
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.finished_product,
                self.warehouse.lot_stock_id,
                lot_id=production.lot_producing_ids,
            ),
            2,
        )

    def test_serial_tracked_finished_goods(self):
        self.finished_product.tracking = "serial"
        production = self._create_mo(qty=1)
        production.action_assign()
        production.action_generate_serial()
        production.button_mark_done()
        storage_move = self._store_move(production)
        self.assertEqual(storage_move.state, "assigned")
        self.assertEqual(
            storage_move.move_line_ids.lot_id, production.lot_producing_ids
        )
        storage_move.picked = True
        storage_move.picking_id.button_validate()
        self.assertEqual(storage_move.state, "done")
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.finished_product,
                self.warehouse.lot_stock_id,
                lot_id=production.lot_producing_ids,
            ),
            1,
        )

    def test_standard_modes_unchanged(self):
        one_step = self.env["stock.warehouse"].create(
            {
                "name": "One Step Test",
                "code": "ONE",
                "manufacture_steps": "mrp_one_step",
            }
        )
        three_step = self.env["stock.warehouse"].create(
            {"name": "Three Step Test", "code": "THR", "manufacture_steps": "pbm_sam"}
        )
        direct_mo = self._create_mo(one_step)
        self.assertFalse(direct_mo.picking_ids)
        self.assertEqual(direct_mo.move_raw_ids.location_id, one_step.lot_stock_id)
        self.assertEqual(
            direct_mo.move_finished_ids.location_dest_id, one_step.lot_stock_id
        )
        three_step_mo = self._create_mo(three_step)
        self.assertTrue(three_step_mo.move_raw_ids.move_orig_ids)
        self.assertFalse(self._store_move(three_step_mo))
        self.assertEqual(len(three_step.pbm_route_id.rule_ids), 3)

    def test_multiple_warehouses_isolated(self):
        other = self.env["stock.warehouse"].create(
            {"name": "Other Warehouse Test", "code": "OTH"}
        )
        self.assertEqual(other.manufacture_steps, "mrp_one_step")
        self.assertFalse(other.pbm_route_id.rule_ids)
        self.assertFalse(other.sam_type_id.active)
        production = self._create_mo()
        self.assertFalse(self._store_move(production))
        self.assertFalse(production.picking_ids)
        self.assertNotEqual(
            other.manu_type_id.default_location_dest_id, self.warehouse.sam_loc_id
        )
        production.action_assign()
        production.qty_producing = production.product_qty
        production.button_mark_done()
        self.assertEqual(
            self._store_move(production).picking_type_id, self.warehouse.sam_type_id
        )

    def test_manual_reservation(self):
        self.warehouse.manu_type_id.reservation_method = "manual"
        production = self._create_mo()
        self.assertEqual(production.move_raw_ids.quantity, 0)
        self.assertFalse(self._store_move(production))
        production.action_assign()
        self.assertEqual(production.move_raw_ids.state, "assigned")
