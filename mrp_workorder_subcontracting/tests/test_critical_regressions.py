from odoo import Command
from odoo.tests import tagged

from .common import WorkorderSubcontractingCommon


@tagged("post_install", "-at_install")
class TestSubcontractingCriticalRegressions(WorkorderSubcontractingCommon):
    def test_01_mixed_standard_po_creates_flow_specific_pickings(self):
        parts_workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        finished_workorder = self._get_workorder(subcontract_parts=False, qty=4.0)
        workorders = parts_workorder | finished_workorder
        purchase_order = self._assign_standard_purchase_order(workorders)

        purchase_order.with_context(skip_subcontract_bid_wizard=True).button_confirm()

        self.assertTrue(purchase_order.has_mixed_subcontract_flows)
        self.assertEqual(len(purchase_order.order_line), 2)
        self.assertEqual(
            parts_workorder.delivery_move_ids.picking_id.picking_type_id,
            self.parts_out_type,
        )
        self.assertEqual(
            finished_workorder.delivery_move_ids.picking_id.picking_type_id,
            self.finished_out_type,
        )
        self.assertFalse(
            any(
                "both parts and finished-product flows" in message.body
                for message in purchase_order.message_ids
            )
        )
        productions = purchase_order.mapped("order_line.workorder_id").production_id
        self.assertFalse(
            any(
                "Subcontract bid confirmed" in message.body
                for message in productions.message_ids
            )
        )

    def test_02_subcontract_pickings_are_not_duplicated_on_reensure(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        purchase_order = self._confirm_standard_purchase_order(workorder)
        delivery_moves = workorder.delivery_move_ids

        purchase_order._ensure_subcontract_pickings()

        self.assertEqual(workorder.delivery_move_ids, delivery_moves)
        self.assertEqual(len(workorder.delivery_move_ids), 1)

    def test_03_purchase_line_sync_preserves_allowed_supplier_set(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        self.assertEqual(
            workorder.subcontract_partner_ids,
            self.partner | self.other_partner,
        )
        purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "date_planned": self.fixed_date,
                "order_type": self.po_type.id,
                "subcontract_location_id": self.subcontract_location.id,
            }
        )

        self.env["purchase.order.line"].create(
            {
                "order_id": purchase_order.id,
                "product_id": self.service.id,
                "product_qty": workorder.qty_remaining,
                "product_uom": self.service.uom_po_id.id,
                "price_unit": 0,
                "date_planned": self.fixed_date,
                "name": "Regression: preserve suppliers",
                "workorder_id": workorder.id,
            }
        )

        self.assertEqual(
            workorder.subcontract_partner_ids,
            self.partner | self.other_partner,
        )

    def test_04_backorder_keeps_subcontract_traceability_links(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        purchase_order = self._confirm_standard_purchase_order(workorder)
        delivery_move = workorder.delivery_move_ids
        self._make_available(self.component, self.stock_location, 20.0)

        backorders = self._validate_picking(
            delivery_move.picking_id, qty_by_move={delivery_move.id: 10.0}
        )

        self.assertEqual(len(backorders), 1)
        self.assertEqual(backorders.move_ids.sub_delivery_workorder_id, workorder)
        self.assertEqual(
            backorders.move_ids.sub_purchase_line_id, purchase_order.order_line
        )
        self.assertEqual(backorders.move_ids.sub_origin_move_id, delivery_move)

    def test_05_unassigned_component_does_not_force_parts_flow(self):
        finished_product = self.env["product.product"].create(
            {
                "name": "Finished Product With Unassigned Component",
                "is_storable": True,
                "uom_id": self.unit.id,
                "uom_po_id": self.unit.id,
            }
        )
        bom = self.env["mrp.bom"].create(
            {
                "product_id": finished_product.id,
                "product_tmpl_id": finished_product.product_tmpl_id.id,
                "product_uom_id": self.unit.id,
                "product_qty": 1.0,
                "type": "normal",
                "operation_ids": [
                    Command.create(
                        {
                            "name": "Subcontract Finished Operation",
                            "workcenter_id": self.env.ref("mrp.mrp_workcenter_3").id,
                            "subcontract_ok": True,
                            "subcontractor_partner_ids": [
                                Command.set((self.partner | self.other_partner).ids)
                            ],
                            "subcontract_product_id": self.service.id,
                        }
                    )
                ],
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": self.component.id,
                            "product_qty": 2.0,
                            "product_uom_id": self.unit.id,
                        }
                    )
                ],
            }
        )
        production = self.env["mrp.production"].create(
            {
                "product_id": finished_product.id,
                "product_uom_id": self.unit.id,
                "product_qty": 10.0,
                "bom_id": bom.id,
                "picking_type_id": self.warehouse.manu_type_id.id,
            }
        )

        production.action_confirm()
        workorder = production.workorder_ids
        raw_move = production.move_raw_ids
        purchase_order = self._assign_standard_purchase_order(workorder)
        purchase_order.with_context(skip_subcontract_bid_wizard=True).button_confirm()

        self.assertFalse(raw_move.operation_id)
        self.assertEqual(raw_move.workorder_id, workorder)
        self.assertFalse(raw_move.sub_component_workorder_id)
        self.assertEqual(workorder.subcontracting_flow, "finished")
        self.assertEqual(workorder.delivery_move_ids.product_id, workorder.product_id)
        self.assertEqual(
            workorder.delivery_move_ids.picking_id.picking_type_id,
            self.finished_out_type,
        )

    def test_06_urgent_moves_for_different_workorders_are_not_merged(self):
        first_workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        second_workorder = self._get_workorder(subcontract_parts=True, qty=5.0)

        self._assign_stock_flow(
            first_workorder,
            "urgent",
            urgent_note="Create first urgent delivery",
        )
        picking = first_workorder.delivery_move_ids.picking_id
        self._assign_stock_flow(
            second_workorder,
            "urgent",
            urgent_note="Reuse urgent delivery picking",
        )

        delivery_moves = picking.move_ids.filtered("sub_delivery_workorder_id")
        self.assertEqual(len(delivery_moves), 2)
        self.assertEqual(
            delivery_moves.mapped("sub_delivery_workorder_id"),
            first_workorder | second_workorder,
        )
        self.assertEqual(first_workorder.delivery_move_ids.product_uom_qty, 20.0)
        self.assertEqual(second_workorder.delivery_move_ids.product_uom_qty, 10.0)

    def test_07_standard_moves_for_different_workorders_are_not_merged(self):
        first_workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        second_workorder = self._get_workorder(subcontract_parts=True, qty=5.0)
        purchase_order = self._assign_standard_purchase_order(
            first_workorder | second_workorder
        )

        purchase_order.with_context(skip_subcontract_bid_wizard=True).button_confirm()

        delivery_moves = (
            first_workorder | second_workorder
        ).delivery_move_ids.filtered("sub_delivery_workorder_id")
        self.assertEqual(len(delivery_moves), 2)
        self.assertEqual(
            set(delivery_moves.mapped("sub_delivery_workorder_id").ids),
            set((first_workorder | second_workorder).ids),
        )
        self.assertEqual(len(delivery_moves.picking_id), 1)
        self.assertEqual(delivery_moves.sub_purchase_line_id.order_id, purchase_order)
        self.assertEqual(first_workorder.delivery_move_ids.product_uom_qty, 20.0)
        self.assertEqual(second_workorder.delivery_move_ids.product_uom_qty, 10.0)

    def test_08_subcontract_fields_prevent_stock_move_merge(self):
        merge_fields = self.env["stock.move"]._prepare_merge_moves_distinct_fields()

        self.assertIn("sub_delivery_workorder_id", merge_fields)
        self.assertIn("sub_return_workorder_id", merge_fields)
        self.assertIn("sub_purchase_line_id", merge_fields)
        self.assertIn("sub_origin_move_id", merge_fields)
        self.assertIn("sub_component_workorder_id", merge_fields)

    def test_09_standard_pickings_can_group_different_purchase_orders(self):
        first_workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        second_workorder = self._get_workorder(subcontract_parts=True, qty=5.0)
        first_purchase_order = self._assign_standard_purchase_order(first_workorder)
        second_purchase_order = self._assign_standard_purchase_order(second_workorder)

        first_purchase_order.with_context(
            skip_subcontract_bid_wizard=True
        ).button_confirm()
        second_purchase_order.with_context(
            skip_subcontract_bid_wizard=True
        ).button_confirm()

        delivery_moves = (
            first_workorder | second_workorder
        ).delivery_move_ids.filtered("sub_delivery_workorder_id")
        self.assertEqual(len(delivery_moves), 2)
        self.assertEqual(len(delivery_moves.picking_id), 1)
        self.assertEqual(
            set(delivery_moves.sub_purchase_line_id.order_id.ids),
            set((first_purchase_order | second_purchase_order).ids),
        )
