from unittest.mock import patch

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import WorkorderSubcontractingCommon


@tagged("post_install", "-at_install")
class TestSubcontractingCoverageBranches(WorkorderSubcontractingCommon):
    def _draft_purchase_order(self, partner=None, order_type=None):
        return self.env["purchase.order"].create(
            {
                "partner_id": (partner or self.partner).id,
                "date_planned": self.fixed_date,
                "order_type": (order_type or self.po_type).id,
                "subcontract_location_id": self.subcontract_location.id,
            }
        )

    def _wizard_values(self, workorder, **extra):
        values = {
            "workorder_ids": [Command.set(workorder.ids)],
            "partner_ids": [Command.set(self.partner.ids)],
            "date_finished": self.fixed_date,
            "flow_type": "standard",
            "create_purchase_order": True,
            "type_id": self.po_type.id,
            "service_id": self.service.id,
        }
        values.update(extra)
        return values

    def test_01_wizard_default_get_rejects_existing_documents(self):
        first_workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        second_workorder = self._get_workorder(subcontract_parts=True, qty=5.0)
        second_workorder.subcontract_partner_ids = [Command.set(self.partner.ids)]
        values = (
            self.env["mrp.workorder.assign.subcontract"]
            .with_context(active_ids=(first_workorder | second_workorder).ids)
            .default_get(["partner_ids"])
        )
        self.assertEqual(values["partner_ids"], [(6, 0, self.partner.ids)])

        self._assign_standard_purchase_order(first_workorder)

        with self.assertRaises(ValidationError):
            self.env["mrp.workorder.assign.subcontract"].with_context(
                active_ids=first_workorder.ids
            ).default_get(["partner_ids", "service_id"])

    def test_02_wizard_onchange_helpers_align_bid_fields(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        purchase_order = self._draft_purchase_order(self.other_partner)
        wizard = self.env["mrp.workorder.assign.subcontract"].new(
            self._wizard_values(
                workorder,
                partner_ids=[Command.set((self.partner | self.other_partner).ids)],
                create_purchase_order=False,
                purchase_order_id=purchase_order.id,
            )
        )

        wizard._onchange_purchase_order_id()
        self.assertEqual(wizard.partner_ids._origin, self.other_partner)

        wizard.partner_ids = self.partner | self.other_partner
        wizard.flow_type = "urgent"
        wizard._onchange_subcontract_bid_rules()
        self.assertEqual(wizard.flow_type, "standard")
        self.assertTrue(wizard.create_purchase_order)
        self.assertFalse(wizard.purchase_order_id)

        wizard.purchase_order_id = purchase_order
        wizard.create_purchase_order = True
        wizard._onchange_create_purchase_order()
        self.assertFalse(wizard.purchase_order_id)

        selection = dict(wizard._get_flow_type_selection())
        self.assertEqual(selection["standard"], "Standard")
        self.assertEqual(selection["urgent"], "Urgent")
        self.assertEqual(selection["subcontractor_stock"], "Subcontractor stock")

    def test_03_wizard_required_field_validations(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        cases = [
            {"partner_ids": [Command.clear()]},
            {"service_id": False},
            {"type_id": False},
        ]
        for extra in cases:
            with self.subTest(extra=extra), self.assertRaises(ValidationError):
                wizard = self.env["mrp.workorder.assign.subcontract"].create(
                    self._wizard_values(workorder, **extra)
                )
                wizard.assign()

        wizard = self.env["mrp.workorder.assign.subcontract"].new(
            self._wizard_values(workorder, date_finished=False)
        )
        with self.assertRaises(ValidationError):
            wizard._validate_required_wizard_fields()

        wizard = self.env["mrp.workorder.assign.subcontract"].new(
            self._wizard_values(
                workorder,
                partner_ids=[Command.set((self.partner | self.other_partner).ids)],
                flow_type="urgent",
                urgent_note="Invalid bid",
            )
        )
        with self.assertRaises(ValidationError):
            wizard._validate_required_wizard_fields()

        wizard = self.env["mrp.workorder.assign.subcontract"].new(
            self._wizard_values(
                workorder,
                partner_ids=[Command.set((self.partner | self.other_partner).ids)],
                flow_type="urgent",
                create_purchase_order=True,
                urgent_note="Invalid purchase options",
            )
        )
        with self.assertRaises(ValidationError):
            wizard._validate_non_standard_flow_fields()

        wizard = self.env["mrp.workorder.assign.subcontract"].new(
            self._wizard_values(workorder, workorder_ids=[Command.clear()])
        )
        with self.assertRaises(ValidationError):
            wizard._validate_selected_workorders()

        workorder.subcontract_ok = False
        wizard = self.env["mrp.workorder.assign.subcontract"].new(
            self._wizard_values(workorder)
        )
        with self.assertRaises(ValidationError):
            wizard._validate_selected_workorders()
        workorder.subcontract_ok = True

        workorder.qty_produced = workorder.qty_production
        workorder.invalidate_recordset(["qty_remaining"])
        wizard = self.env["mrp.workorder.assign.subcontract"].new(
            self._wizard_values(workorder)
        )
        with self.assertRaises(ValidationError):
            wizard._validate_selected_workorders()

        other_warehouse = self.env["stock.warehouse"].create(
            {"name": "Second Test Warehouse", "code": "STW"}
        )
        other_warehouse.write(
            {
                "sub_out_picking_type_id": self.parts_out_type.id,
                "sub_in_picking_type_id": self.parts_in_type.id,
                "sub_out_virtual_picking_type_id": self.finished_out_type.id,
                "sub_in_virtual_picking_type_id": self.finished_in_type.id,
            }
        )
        other_production = self.env["mrp.production"].create(
            {
                "product_id": self.finished_parts.id,
                "product_uom_id": self.unit.id,
                "product_qty": 5.0,
                "bom_id": self.parts_bom.id,
                "picking_type_id": other_warehouse.manu_type_id.id,
            }
        )
        other_production.action_confirm()
        wizard = self.env["mrp.workorder.assign.subcontract"].new(
            self._wizard_values(workorder | other_production.workorder_ids[:1])
        )
        with self.assertRaises(ValidationError):
            wizard._validate_selected_workorders()

    def test_04_wizard_standard_existing_purchase_order_validations(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        purchase_order = self._draft_purchase_order(self.other_partner)
        cases = [
            {"create_purchase_order": False},
            {
                "create_purchase_order": False,
                "purchase_order_id": purchase_order.id,
            },
        ]
        for extra in cases:
            with self.subTest(extra=extra), self.assertRaises(ValidationError):
                wizard = self.env["mrp.workorder.assign.subcontract"].create(
                    self._wizard_values(workorder, **extra)
                )
                wizard.assign()

        wizard = self.env["mrp.workorder.assign.subcontract"].new(
            self._wizard_values(
                workorder,
                create_purchase_order=False,
                partner_ids=[Command.set((self.partner | self.other_partner).ids)],
                purchase_order_id=purchase_order.id,
            )
        )
        with self.assertRaises(ValidationError):
            wizard._validate_standard_flow_fields()

        wizard = self.env["mrp.workorder.assign.subcontract"].new(
            self._wizard_values(
                workorder,
                create_purchase_order=False,
                partner_ids=[Command.set((self.partner | self.other_partner).ids)],
                purchase_order_id=purchase_order.id,
            )
        )
        with self.assertRaises(ValidationError):
            wizard._validate_existing_purchase_order_supplier()

    def test_05_wizard_rejects_duplicate_documents(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        self._assign_standard_purchase_order(workorder)
        with self.assertRaises(ValidationError):
            self._create_standard_wizard(workorder).assign()

        urgent_workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        self._assign_stock_flow(
            urgent_workorder, "urgent", urgent_note="Already delivered"
        )
        with self.assertRaises(ValidationError):
            self._assign_stock_flow(
                urgent_workorder, "urgent", urgent_note="Duplicate delivery"
            )

        stock_workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        self._assign_stock_flow(stock_workorder, "subcontractor_stock")
        with self.assertRaises(ValidationError):
            self._assign_stock_flow(stock_workorder, "subcontractor_stock")

    def test_06_wizard_configuration_validation_branches(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        checks = [
            ("sub_out_picking_type_id", "urgent"),
            ("sub_in_picking_type_id", "urgent"),
            ("sub_out_virtual_picking_type_id", "urgent"),
            ("sub_in_virtual_picking_type_id", "urgent"),
        ]
        for field_name, flow_type in checks:
            with self.subTest(field_name=field_name), self.env.cr.savepoint():
                self.warehouse[field_name] = False
                with self.assertRaises(ValidationError):
                    self._assign_stock_flow(
                        workorder,
                        flow_type,
                        urgent_note="Missing warehouse configuration",
                    )
                self._configure_warehouse()

    def test_07_purchase_order_type_configuration_branches(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        purchase_order = self._draft_purchase_order()
        wizard = self.env["mrp.workorder.assign.subcontract"].new(
            self._wizard_values(workorder, type_id=False)
        )
        wizard._validate_purchase_order_type_configuration()

        with self.env.cr.savepoint():
            purchase_order.order_type = False
            wizard = self.env["mrp.workorder.assign.subcontract"].new(
                self._wizard_values(
                    workorder,
                    create_purchase_order=False,
                    purchase_order_id=purchase_order.id,
                )
            )
            with self.assertRaises(ValidationError):
                wizard._validate_purchase_order_type_configuration()

        with self.env.cr.savepoint():
            purchase_type = self.po_type.copy({"is_subcontracting": False})
            wizard = self.env["mrp.workorder.assign.subcontract"].new(
                self._wizard_values(workorder, type_id=purchase_type.id)
            )
            with self.assertRaises(ValidationError):
                wizard._validate_purchase_order_type_configuration()

        for field_name in ("sub_out_picking_type_id", "sub_in_picking_type_id"):
            with self.subTest(field_name=field_name):
                picking_type = self.po_type[field_name]
                self.po_type[field_name] = False
                wizard = self.env["mrp.workorder.assign.subcontract"].new(
                    self._wizard_values(workorder)
                )
                with self.assertRaises(ValidationError):
                    wizard._validate_purchase_order_type_configuration()
                self.po_type[field_name] = picking_type

    def test_07_existing_purchase_order_standard_flow_is_used(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        purchase_order = self._draft_purchase_order()
        wizard = self.env["mrp.workorder.assign.subcontract"].create(
            self._wizard_values(
                workorder,
                create_purchase_order=False,
                purchase_order_id=purchase_order.id,
            )
        )

        action = wizard.assign()

        self.assertEqual(action["res_id"], purchase_order.id)
        self.assertEqual(workorder.purchase_order_line_ids.order_id, purchase_order)

    def test_08_urgent_flow_can_create_linked_purchase_order_line(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        purchase_order = self._draft_purchase_order()
        wizard = self.env["mrp.workorder.assign.subcontract"].create(
            self._wizard_values(
                workorder,
                flow_type="urgent",
                create_purchase_order=False,
                purchase_order_id=purchase_order.id,
                urgent_note="Urgent linked to existing purchase",
            )
        )

        wizard.assign()

        line = workorder.purchase_order_line_ids
        self.assertEqual(line.order_id, purchase_order)
        self.assertEqual(workorder.delivery_move_ids.sub_purchase_line_id, line)

        duplicated = self.env["mrp.workorder.assign.subcontract"].create(
            self._wizard_values(
                workorder,
                flow_type="urgent",
                create_purchase_order=False,
                purchase_order_id=purchase_order.id,
                urgent_note="Duplicate urgent link",
            )
        )
        with self.assertRaises(ValidationError):
            duplicated.assign()

    def test_09_purchase_order_bid_wizard_and_competitor_resolution(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        wizard = self.env["mrp.workorder.assign.subcontract"].create(
            self._wizard_values(
                workorder,
                partner_ids=[Command.set((self.partner | self.other_partner).ids)],
            )
        )
        wizard.assign()
        purchase_orders = workorder.purchase_order_line_ids.order_id
        winner = purchase_orders.filtered(
            lambda order: order.partner_id == self.partner
        )
        competitor = purchase_orders - winner

        action = winner.button_confirm()
        self.assertEqual(action["res_model"], "purchase.order.subcontract.bid.wizard")

        bid_wizard = self.env[action["res_model"]].browse(action["res_id"])
        self.assertIn(competitor.display_name, bid_wizard.summary_html)
        bid_wizard.action_confirm_bid()

        self.assertEqual(winner.state, "purchase")
        self.assertEqual(competitor.state, "cancel")
        self.assertTrue(
            any(
                winner.display_name in message.body
                and 'data-oe-model="purchase.order"' in message.body
                for message in competitor.message_ids
            )
        )
        self.assertTrue(
            any(
                "Subcontract bid confirmed" in message.body
                for message in workorder.production_id.message_ids
            )
        )

    def test_10_purchase_order_rejects_already_won_bid(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        wizard = self.env["mrp.workorder.assign.subcontract"].create(
            self._wizard_values(
                workorder,
                partner_ids=[Command.set((self.partner | self.other_partner).ids)],
            )
        )
        wizard.assign()
        purchase_orders = workorder.purchase_order_line_ids.order_id
        winner = purchase_orders.filtered(
            lambda order: order.partner_id == self.partner
        )
        competitor = purchase_orders - winner

        winner.with_context(skip_subcontract_bid_wizard=True).button_confirm()

        with self.assertRaises(ValidationError):
            competitor.with_context(skip_subcontract_bid_wizard=True).button_confirm()

    def test_11_purchase_order_partial_competitor_lost_bid_is_locked(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        other_workorder = self._get_workorder(subcontract_parts=True, qty=5.0)
        wizard = self.env["mrp.workorder.assign.subcontract"].create(
            self._wizard_values(
                workorder,
                partner_ids=[Command.set((self.partner | self.other_partner).ids)],
            )
        )
        wizard.assign()
        purchase_orders = workorder.purchase_order_line_ids.order_id
        winner = purchase_orders.filtered(
            lambda order: order.partner_id == self.partner
        )
        competitor = purchase_orders - winner
        self.env["purchase.order.line"].create(
            {
                "order_id": competitor.id,
                "product_id": self.service.id,
                "product_qty": other_workorder.qty_remaining,
                "product_uom": self.service.uom_po_id.id,
                "price_unit": 0,
                "date_planned": self.fixed_date,
                "name": "Non losing line",
                "workorder_id": other_workorder.id,
            }
        )

        winner.with_context(skip_subcontract_bid_wizard=True).button_confirm()

        lost_line = competitor.order_line.filtered(
            lambda line: line.workorder_id == workorder
        )
        self.assertEqual(competitor.state, "draft")
        self.assertTrue(lost_line.subcontract_lost_bid)
        self.assertEqual(lost_line.product_qty, 0.0)
        self.assertTrue(
            any(
                "<ul>" in message.body and winner.display_name in message.body
                for message in competitor.message_ids
            )
        )
        with self.assertRaises(ValidationError):
            lost_line.product_qty = 1.0

    def test_12_purchase_line_quantities_and_sync_branches(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        purchase_order = self._confirm_standard_purchase_order(workorder)
        line = purchase_order.order_line
        self.assertEqual(line._get_subcontract_target_receipt_qty(), 0.0)
        delivery_move = workorder.delivery_move_ids
        self._make_available(self.component, self.stock_location, 20.0)
        self._validate_picking(
            delivery_move.picking_id,
            qty_by_move={delivery_move.id: 10.0},
        )

        self.assertEqual(line._get_subcontract_delivery_done_qty(), 10.0)
        self.assertEqual(line._get_subcontract_target_receipt_qty(), 5.0)
        self.assertEqual(line._get_subcontract_receipt_qty(), 5.0)

        mixed_workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        mixed_purchase_order = self._confirm_standard_purchase_order(mixed_workorder)
        mixed_line = mixed_purchase_order.order_line
        mixed_picking = mixed_workorder.delivery_move_ids.picking_id
        half_unit = self.env["uom.uom"].create(
            {
                "name": "Half Unit",
                "category_id": self.unit.category_id.id,
                "uom_type": "smaller",
                "factor": 2.0,
                "rounding": 0.01,
            }
        )
        extra_move = self.env["stock.move"].create(
            {
                "name": self.component.display_name,
                "product_id": self.component.id,
                "product_uom": half_unit.id,
                "product_uom_qty": 24.0,
                "location_id": mixed_picking.location_id.id,
                "location_dest_id": mixed_picking.location_dest_id.id,
                "picking_id": mixed_picking.id,
                "origin": mixed_purchase_order.name,
                "company_id": mixed_picking.company_id.id,
                "warehouse_id": mixed_picking.picking_type_id.warehouse_id.id,
                "sub_purchase_line_id": mixed_line.id,
                "sub_delivery_workorder_id": mixed_workorder.id,
            }
        )
        extra_move._action_confirm()
        mixed_moves = mixed_workorder.delivery_move_ids
        self._make_available(self.component, self.stock_location, 32.0)
        self._validate_picking(
            mixed_picking,
            qty_by_move={
                (mixed_moves - extra_move).id: 10.0,
                extra_move.id: 12.0,
            },
        )
        self.assertEqual(mixed_line._get_subcontract_target_receipt_qty(), 5.0)

        workorder.return_move_ids.write({"sub_purchase_line_id": False})
        line._sync_existing_subcontract_documents()
        self.assertEqual(workorder.return_move_ids.sub_purchase_line_id, line)

    def test_13_purchase_line_write_unlinks_old_subcontract_documents(self):
        old_workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        new_workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        purchase_order = self._confirm_standard_purchase_order(old_workorder)
        line = purchase_order.order_line
        delivery_move = old_workorder.delivery_move_ids

        line.workorder_id = new_workorder

        self.assertFalse(delivery_move.sub_purchase_line_id)
        self.assertEqual(line.workorder_id, new_workorder)

    def test_14_purchase_line_rejects_supplier_mismatch_with_moves(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        self._assign_stock_flow(
            workorder, "urgent", urgent_note="Create supplier specific moves"
        )
        purchase_order = self._draft_purchase_order(self.other_partner)

        with self.assertRaises(ValidationError):
            self.env["purchase.order.line"].create(
                {
                    "order_id": purchase_order.id,
                    "product_id": self.service.id,
                    "product_qty": workorder.qty_remaining,
                    "product_uom": self.service.uom_po_id.id,
                    "price_unit": 0,
                    "date_planned": self.fixed_date,
                    "name": "Wrong supplier",
                    "workorder_id": workorder.id,
                }
            )

    def test_15_workorder_supplier_consistency_and_no_operation_sync(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        other_workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        self._assign_stock_flow(
            workorder, "urgent", urgent_note="Create first supplier move"
        )
        self._assign_stock_flow(
            other_workorder,
            "urgent",
            partner=self.other_partner,
            urgent_note="Create second supplier move",
        )
        other_workorder.delivery_move_ids.write(
            {"sub_delivery_workorder_id": workorder.id}
        )
        with self.assertRaises(ValidationError):
            workorder._check_subcontract_supplier_consistency()

        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        workorder.subcontract_product_id = False
        workorder._sync_subcontracting_from_operation()
        self.assertEqual(workorder.subcontract_product_id, self.service)
        self._assign_stock_flow(
            workorder,
            "subcontractor_stock",
            urgent_note=False,
        )
        workorder.subcontract_product_id = False
        workorder._sync_subcontracting_from_operation()
        self.assertFalse(workorder.subcontract_product_id)

    def test_16_workorder_state_and_quantity_helper_branches(self):
        workorder = self._get_workorder(subcontract_parts=False, qty=6.0)
        self.assertEqual(workorder.subcontract_state, "none")
        self._assign_stock_flow(
            workorder,
            "urgent",
            urgent_note="Finished product helper branch",
        )
        delivery_move = workorder.delivery_move_ids
        self._make_available(
            workorder.product_id,
            delivery_move.picking_id.location_id,
            delivery_move.product_uom_qty,
        )
        self._validate_picking(
            delivery_move.picking_id,
            qty_by_move={delivery_move.id: 3.0},
        )

        self.assertEqual(workorder._get_subcontract_delivery_done_qty(), 3.0)
        self.assertEqual(workorder._get_subcontract_target_return_qty(), 3.0)
        self.assertEqual(workorder._get_subcontract_return_qty(), 3.0)

    def test_17_workorder_subcontract_actions(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        create_action = workorder.button_create_subcontract_order()
        self.assertEqual(create_action["res_model"], "mrp.workorder.assign.subcontract")
        self.assertEqual(
            create_action["context"]["default_workorder_ids"], workorder.ids
        )

        empty_purchase_action = workorder.action_view_subcontract_purchase_orders()
        empty_transfer_action = workorder.action_view_subcontract_transfers()
        self.assertEqual(empty_purchase_action["domain"], [("id", "in", [])])
        self.assertEqual(empty_transfer_action["domain"], [("id", "in", [])])
        self.assertEqual(empty_transfer_action["context"]["expand"], 1)

        purchase_order = self._confirm_standard_purchase_order(workorder)
        purchase_action = workorder.action_view_subcontract_purchase_orders()
        transfer_action = workorder.action_view_subcontract_transfers()
        self.assertEqual(purchase_action["res_id"], purchase_order.id)
        self.assertEqual(
            transfer_action["domain"], [("id", "in", workorder.delivery_move_ids.ids)]
        )
        self.assertEqual(transfer_action["context"]["expand"], 1)

        other_purchase_order = self._assign_standard_purchase_order(
            self._get_workorder(subcontract_parts=True, qty=5.0)
        )
        workorder.purchase_order_line_ids |= other_purchase_order.order_line
        purchase_action = workorder.action_view_subcontract_purchase_orders()
        self.assertEqual(
            purchase_action["domain"],
            [("id", "in", (purchase_order | other_purchase_order).ids)],
        )

    def test_17_mrp_production_subcontract_actions(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        production = workorder.production_id
        purchase_order = self._confirm_standard_purchase_order(workorder)

        purchase_action = production.action_view_subcontract_purchase_orders()
        transfer_action = production.action_view_subcontract_transfers()

        self.assertEqual(purchase_action["res_id"], purchase_order.id)
        self.assertEqual(transfer_action["res_model"], "stock.move")
        self.assertEqual(
            transfer_action["domain"], [("id", "in", workorder.delivery_move_ids.ids)]
        )
        self.assertEqual(transfer_action["context"]["expand"], 1)

        other_workorder = self._get_workorder(subcontract_parts=True, qty=5.0)
        other_po = self._assign_standard_purchase_order(other_workorder)
        combined = production | other_workorder.production_id
        self.assertEqual(len(purchase_order | other_po), 2)
        self.assertTrue(combined)

    def test_18_stock_picking_and_stock_move_fallback_branches(self):
        normal_picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.warehouse.int_type_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        self.assertFalse(normal_picking.subcontract_parts)

        move_without_picking = self.env["stock.move"].create(
            {
                "name": self.component.display_name,
                "product_id": self.component.id,
                "product_uom": self.unit.id,
                "product_uom_qty": 1.0,
                "location_id": self.stock_location.id,
                "location_dest_id": self.subcontract_location.id,
            }
        )
        self.assertFalse(move_without_picking.action_open_subcontract_picking())

    def test_19_wizard_rejects_missing_subcontract_locations(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        partner = self.env["res.partner"].create({"name": "No Location Supplier"})
        picking_type = self.env["stock.picking.type"].new(
            {
                "name": "Missing Location Type",
                "code": "outgoing",
                "sequence_code": "TEST/MISSING",
                "default_location_src_id": False,
                "default_location_dest_id": False,
            }
        )
        warehouse = self.env["stock.warehouse"].new(
            {"sub_out_picking_type_id": picking_type}
        )
        wizard = self.env["mrp.workorder.assign.subcontract"].new(
            self._wizard_values(
                workorder, flow_type="urgent", urgent_note="Missing source location"
            )
        )

        with (
            patch.object(
                type(wizard), "_get_workorder_warehouses", return_value=warehouse
            ),
            self.assertRaises(ValidationError),
        ):
            wizard._get_picking_config(workorder, partner)

    def test_19_stock_picking_missing_incoming_configuration(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        self._assign_stock_flow(
            workorder, "urgent", urgent_note="Missing incoming configuration"
        )
        delivery_move = workorder.delivery_move_ids
        self._make_available(self.component, self.stock_location, 20.0)

        with self.env.cr.savepoint(), self.assertRaises(ValidationError):
            self.warehouse.sub_in_picking_type_id = False
            self._validate_picking(
                delivery_move.picking_id,
                qty_by_move={delivery_move.id: 20.0},
                cancel_backorder=True,
            )
        self._configure_warehouse()
