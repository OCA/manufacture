from odoo.tests import tagged

from .common import WorkorderSubcontractingCommon


@tagged("post_install", "-at_install")
class TestSubcontractingStockLocations(WorkorderSubcontractingCommon):
    def _available_quantity(self, product, location):
        return self.env["stock.quant"]._get_available_quantity(product, location)

    def test_01_parts_out_moves_stock_to_subcontractor_location(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        self._assign_stock_flow(
            workorder,
            "urgent",
            urgent_note="Check subcontractor stock location",
        )
        delivery_move = workorder.delivery_move_ids
        initial_qty = self._available_quantity(
            self.component, self.subcontract_location
        )
        self._make_available(self.component, self.stock_location, 20.0)

        self._validate_picking(
            delivery_move.picking_id,
            qty_by_move={delivery_move.id: 20.0},
            cancel_backorder=True,
        )

        self.assertEqual(
            self._available_quantity(self.component, self.subcontract_location),
            initial_qty + 20.0,
        )

    def test_02_parts_return_uses_virtual_source_to_avoid_subcontractor_negative(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        purchase_order = self._confirm_standard_purchase_order(
            workorder, purchase_type=self.po_type_instant
        )

        return_move = workorder.return_move_ids
        self.assertEqual(return_move.picking_id.picking_type_id, self.parts_in_type)
        self.assertEqual(
            return_move.picking_id.location_id, self.virtual_subcontract_location
        )
        self.assertEqual(
            return_move.picking_id.location_id.usage,
            "production",
        )
        self.assertNotEqual(
            return_move.picking_id.location_id, self.subcontract_location
        )
        self.assertEqual(return_move.sub_purchase_line_id, purchase_order.order_line)

    def test_03_standard_parts_confirmation_syncs_raw_moves_to_subcontractor(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)

        self._confirm_standard_purchase_order(workorder)

        self.assertTrue(workorder.move_raw_ids)
        self.assertEqual(workorder.move_raw_ids.location_id, self.subcontract_location)

    def test_04_finished_flow_keeps_raw_move_location_sync_out_of_scope(self):
        workorder = self._get_workorder(subcontract_parts=False, qty=5.0)

        self._assign_stock_flow(
            workorder,
            "urgent",
            urgent_note="Finished flow location check",
        )

        delivery_move = workorder.delivery_move_ids
        self.assertFalse(workorder.move_raw_ids)
        self.assertEqual(
            delivery_move.picking_id.picking_type_id, self.finished_out_type
        )
        self.assertEqual(
            delivery_move.picking_id.location_dest_id, self.virtual_subcontract_location
        )
        self.assertEqual(delivery_move.product_id, workorder.product_id)
