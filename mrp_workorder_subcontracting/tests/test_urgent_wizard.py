from odoo.tests import tagged

from .common import WorkorderSubcontractingCommon


@tagged("post_install", "-at_install")
class TestSubcontractingUrgentWizard(WorkorderSubcontractingCommon):
    def test_01_urgent_parts_creates_out_and_logs_reason(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)

        self._assign_stock_flow(
            workorder,
            "urgent",
            urgent_note="Customer requested immediate subcontracting",
        )

        delivery_move = workorder.delivery_move_ids
        self.assertEqual(len(delivery_move), 1)
        self.assertEqual(workorder.subcontract_flow_type, "urgent")
        self.assertEqual(workorder.subcontract_partner_ids, self.partner)
        self.assertEqual(workorder.move_raw_ids.location_id, self.subcontract_location)
        self.assertEqual(delivery_move.product_id, self.component)
        self.assertEqual(delivery_move.product_uom_qty, 20.0)
        self.assertFalse(delivery_move.sub_purchase_line_id)
        self.assertEqual(delivery_move.picking_id.picking_type_id, self.parts_out_type)
        self.assertEqual(delivery_move.picking_id.location_id, self.stock_location)
        self.assertEqual(
            delivery_move.picking_id.location_dest_id, self.subcontract_location
        )
        self.assertTrue(
            any(
                "Customer requested immediate subcontracting" in message.body
                for message in workorder.production_id.message_ids
            )
        )

    def test_02_urgent_parts_partial_out_creates_partial_return_without_po(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        self._assign_stock_flow(
            workorder,
            "urgent",
            urgent_note="Need partial subcontracting shipment",
        )
        delivery_move = workorder.delivery_move_ids
        self._make_available(self.component, self.stock_location, 20.0)

        backorders = self._validate_picking(
            delivery_move.picking_id, qty_by_move={delivery_move.id: 10.0}
        )

        return_move = workorder.return_move_ids
        self.assertEqual(len(return_move), 1)
        self.assertEqual(return_move.product_id, workorder.product_id)
        self.assertEqual(return_move.product_uom_qty, 5.0)
        self.assertEqual(return_move.picking_id.picking_type_id, self.parts_in_type)
        self.assertFalse(return_move.sub_purchase_line_id)
        self.assertEqual(return_move.picking_id.partner_id, self.partner)

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
        self.assertFalse(return_moves.sub_purchase_line_id)

    def test_03_urgent_finished_partial_out_returns_finished_quantity(self):
        workorder = self._get_workorder(subcontract_parts=False, qty=6.0)
        self._assign_stock_flow(
            workorder,
            "urgent",
            urgent_note="Finished product must be subcontracted urgently",
        )
        delivery_move = workorder.delivery_move_ids
        self._make_available(
            workorder.product_id,
            delivery_move.picking_id.location_id,
            delivery_move.product_uom_qty,
        )

        self._validate_picking(
            delivery_move.picking_id, qty_by_move={delivery_move.id: 2.0}
        )

        return_move = workorder.return_move_ids
        self.assertEqual(
            delivery_move.picking_id.picking_type_id, self.finished_out_type
        )
        self.assertEqual(return_move.product_uom_qty, 2.0)
        self.assertEqual(return_move.picking_id.picking_type_id, self.finished_in_type)
        self.assertEqual(
            return_move.picking_id.location_id, self.virtual_subcontract_location
        )
