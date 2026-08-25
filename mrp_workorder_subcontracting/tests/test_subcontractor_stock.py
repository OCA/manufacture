from odoo.tests import tagged

from .common import WorkorderSubcontractingCommon


@tagged("post_install", "-at_install")
class TestSubcontractingSubcontractorStock(WorkorderSubcontractingCommon):
    def test_01_subcontractor_stock_parts_creates_in_only(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)

        self._assign_stock_flow(workorder, "subcontractor_stock")

        self.assertEqual(workorder.subcontract_flow_type, "subcontractor_stock")
        self.assertFalse(workorder.delivery_move_ids)
        return_move = workorder.return_move_ids
        self.assertEqual(len(return_move), 1)
        self.assertEqual(return_move.product_id, workorder.product_id)
        self.assertEqual(return_move.product_uom_qty, 10.0)
        self.assertFalse(return_move.sub_purchase_line_id)
        self.assertEqual(return_move.picking_id.partner_id, self.partner)
        self.assertEqual(return_move.picking_id.picking_type_id, self.parts_in_type)
        self.assertEqual(
            return_move.picking_id.location_id, self.virtual_subcontract_location
        )
        self.assertEqual(workorder.move_raw_ids.location_id, self.subcontract_location)

    def test_02_subcontractor_stock_finished_uses_finished_virtual_in(self):
        workorder = self._get_workorder(subcontract_parts=False, qty=4.0)

        self._assign_stock_flow(workorder, "subcontractor_stock")

        return_move = workorder.return_move_ids
        self.assertEqual(len(return_move), 1)
        self.assertEqual(return_move.product_id, workorder.product_id)
        self.assertEqual(return_move.product_uom_qty, 4.0)
        self.assertEqual(return_move.picking_id.picking_type_id, self.finished_in_type)
        self.assertEqual(
            return_move.picking_id.location_id, self.virtual_subcontract_location
        )

    def test_03_done_subcontractor_stock_receipt_completes_workorder(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        self._assign_stock_flow(workorder, "subcontractor_stock")
        return_move = workorder.return_move_ids
        self._make_available(self.component, self.subcontract_location, 20.0)

        self._validate_picking(
            return_move.picking_id,
            qty_by_move={return_move.id: return_move.product_uom_qty},
            cancel_backorder=True,
        )

        self.assertEqual(return_move.state, "done")
        self.assertEqual(workorder.state, "done")
        self.assertEqual(workorder.subcontract_state, "done")
