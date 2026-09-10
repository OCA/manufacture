from odoo.tests import tagged

from .common import WorkorderSubcontractingCommon


@tagged("post_install", "-at_install")
class TestSubcontractingClosureExceptions(WorkorderSubcontractingCommon):
    def test_01_cancelled_delivery_without_receipt_sets_exception(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        self._assign_stock_flow(
            workorder,
            "urgent",
            urgent_note="Delivery will be cancelled before any receipt",
        )

        workorder.delivery_move_ids.picking_id.action_cancel()

        self.assertTrue(workorder.subcontract_exception)
        self.assertTrue(workorder.subcontract_exception_message)
        self.assertEqual(workorder.subcontract_state, "exception")
        self.assertTrue(
            any(
                "Subcontract exception" in message.body
                for message in workorder.production_id.message_ids
            )
        )

    def test_02_open_return_keeps_workorder_in_logistics(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)

        self._assign_stock_flow(workorder, "subcontractor_stock")

        self.assertFalse(workorder.subcontract_exception)
        self.assertEqual(workorder.subcontract_state, "logistics")
        self.assertIn(workorder.return_move_ids.state, ("confirmed", "assigned"))

    def test_03_completed_receipt_clears_existing_exception(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        self._assign_stock_flow(
            workorder,
            "urgent",
            urgent_note="Create an exception and then clear it manually",
        )
        workorder.delivery_move_ids.picking_id.action_cancel()
        self.assertTrue(workorder.subcontract_exception)

        self._assign_stock_flow(workorder, "subcontractor_stock")
        return_move = workorder.return_move_ids.filtered(
            lambda move: move.state != "cancel"
        )
        self._make_available(self.component, self.subcontract_location, 20.0)
        self._validate_picking(
            return_move.picking_id,
            qty_by_move={return_move.id: return_move.product_uom_qty},
            cancel_backorder=True,
        )

        self.assertFalse(workorder.subcontract_exception)
        self.assertFalse(workorder.subcontract_exception_message)
        self.assertEqual(workorder.state, "done")
        self.assertEqual(workorder.subcontract_state, "done")
