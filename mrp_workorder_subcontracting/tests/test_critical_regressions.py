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
        self.assertTrue(
            any(
                "both parts and finished-product flows" in message.body
                for message in purchase_order.message_ids
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
