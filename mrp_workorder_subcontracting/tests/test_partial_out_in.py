from odoo.tests import tagged

from .common import WorkorderSubcontractingCommon


@tagged("post_install", "-at_install")
class TestSubcontractingPartialOutIn(WorkorderSubcontractingCommon):
    def test_01_standard_partial_out_creates_partial_in(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        purchase_order = self._confirm_standard_purchase_order(workorder)
        delivery_move = workorder.delivery_move_ids
        self._make_available(self.component, self.stock_location, 20.0)

        backorders = self._validate_picking(
            delivery_move.picking_id, qty_by_move={delivery_move.id: 10.0}
        )

        self.assertEqual(len(backorders), 1)
        self.assertEqual(workorder.return_move_ids.product_uom_qty, 5.0)
        self.assertEqual(
            workorder.return_move_ids.sub_purchase_line_id, purchase_order.order_line
        )
        self.assertEqual(
            workorder.return_move_ids.picking_id.picking_type_id, self.parts_in_type
        )
        self.assertEqual(
            workorder.return_move_ids.picking_id.location_id,
            self.virtual_subcontract_location,
        )
        self.assertEqual(backorders.move_ids.sub_delivery_workorder_id, workorder)
        self.assertEqual(
            backorders.move_ids.sub_purchase_line_id, purchase_order.order_line
        )

    def test_02_standard_second_out_feeds_existing_open_in(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        self._confirm_standard_purchase_order(workorder)
        delivery_move = workorder.delivery_move_ids
        self._make_available(self.component, self.stock_location, 20.0)

        backorders = self._validate_picking(
            delivery_move.picking_id, qty_by_move={delivery_move.id: 10.0}
        )
        self.assertEqual(len(backorders), 1)
        first_in_picking = workorder.return_move_ids.picking_id

        backorder_move = backorders.move_ids.filtered(
            lambda move: move.sub_delivery_workorder_id == workorder
        )
        self._validate_picking(
            backorders, qty_by_move={backorder_move.id: 10.0}, cancel_backorder=True
        )

        return_moves = workorder.return_move_ids.filtered(
            lambda move: move.state != "cancel"
        )
        self.assertEqual(len(return_moves), 1)
        self.assertEqual(return_moves.product_uom_qty, 10.0)
        self.assertEqual(return_moves.picking_id, first_in_picking)
        self.assertIn(first_in_picking.state, ("confirmed", "assigned"))

    def test_03_done_in_with_closed_documents_completes_workorder(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        self._confirm_standard_purchase_order(workorder)
        delivery_move = workorder.delivery_move_ids
        self._make_available(self.component, self.stock_location, 20.0)
        backorders = self._validate_picking(
            delivery_move.picking_id, qty_by_move={delivery_move.id: 10.0}
        )
        backorders.action_cancel()

        receipt_move = workorder.return_move_ids
        self._validate_picking(
            receipt_move.picking_id,
            qty_by_move={receipt_move.id: receipt_move.product_uom_qty},
            cancel_backorder=True,
        )

        self.assertEqual(workorder.state, "done")
        self.assertEqual(workorder.subcontract_state, "done")
