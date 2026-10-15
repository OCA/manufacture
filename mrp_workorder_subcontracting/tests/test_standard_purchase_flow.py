from odoo.tests import tagged

from .common import WorkorderSubcontractingCommon


@tagged("post_install", "-at_install")
class TestSubcontractingStandardPurchaseFlow(WorkorderSubcontractingCommon):
    def test_01_standard_wizard_creates_purchase_order_line(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        purchase_order = self._assign_standard_purchase_order(workorder)
        line = purchase_order.order_line

        self.assertEqual(purchase_order.partner_id, self.partner)
        self.assertEqual(purchase_order.order_type, self.po_type)
        self.assertEqual(
            purchase_order.subcontract_location_id, self.subcontract_location
        )
        self.assertEqual(line.workorder_id, workorder)
        self.assertEqual(line.product_id, self.service)
        self.assertEqual(line.product_qty, workorder.qty_remaining)
        self.assertEqual(workorder.subcontract_flow_type, "standard")
        self.assertEqual(workorder.subcontract_product_id, self.service)
        self.assertEqual(workorder.subcontract_partner_ids, self.partner)
        self.assertEqual(workorder.subcontract_state, "rfq")

    def test_02_standard_purchase_confirmation_creates_parts_out(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        purchase_order = self._assign_standard_purchase_order(workorder)

        purchase_order.with_context(skip_subcontract_bid_wizard=True).button_confirm()

        self.assertEqual(purchase_order.state, "purchase")
        self.assertEqual(workorder.subcontract_state, "logistics")
        self.assertEqual(workorder.move_raw_ids.location_id, self.subcontract_location)
        delivery_moves = workorder.delivery_move_ids
        self.assertEqual(len(delivery_moves), 1)
        self.assertEqual(delivery_moves.product_id, self.component)
        self.assertEqual(delivery_moves.product_uom_qty, 20.0)
        self.assertEqual(delivery_moves.sub_purchase_line_id, purchase_order.order_line)
        picking = delivery_moves.picking_id
        self.assertEqual(picking.partner_id, self.partner)
        self.assertEqual(picking.picking_type_id, self.parts_out_type)
        self.assertEqual(
            picking.location_id, self.parts_out_type.default_location_src_id
        )
        self.assertEqual(picking.location_dest_id, self.subcontract_location)
        self.assertFalse(workorder.return_move_ids)

    def test_03_immediate_return_creates_parts_in_on_purchase_confirmation(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        purchase_order = self._assign_standard_purchase_order(
            workorder, purchase_type=self.po_type_instant
        )

        purchase_order.with_context(skip_subcontract_bid_wizard=True).button_confirm()

        self.assertEqual(purchase_order.state, "purchase")
        self.assertEqual(len(workorder.delivery_move_ids), 1)
        return_moves = workorder.return_move_ids
        self.assertEqual(len(return_moves), 1)
        self.assertEqual(return_moves.product_id, workorder.product_id)
        self.assertEqual(return_moves.product_uom_qty, 10.0)
        self.assertEqual(return_moves.sub_purchase_line_id, purchase_order.order_line)
        self.assertEqual(return_moves.picking_id.picking_type_id, self.parts_in_type)
        self.assertEqual(
            return_moves.picking_id.location_id, self.virtual_subcontract_location
        )

    def test_04_standard_finished_flow_uses_virtual_outgoing_type(self):
        workorder = self._get_workorder(subcontract_parts=False, qty=5.0)
        purchase_order = self._assign_standard_purchase_order(workorder)

        purchase_order.with_context(skip_subcontract_bid_wizard=True).button_confirm()

        delivery_moves = workorder.delivery_move_ids
        self.assertEqual(len(delivery_moves), 1)
        self.assertEqual(delivery_moves.product_id, workorder.product_id)
        self.assertEqual(delivery_moves.product_uom_qty, 5.0)
        self.assertEqual(
            delivery_moves.picking_id.picking_type_id, self.finished_out_type
        )
        self.assertEqual(
            delivery_moves.picking_id.location_dest_id,
            self.virtual_subcontract_location,
        )
        self.assertFalse(workorder.return_move_ids)

    def test_05_multiple_suppliers_create_multiple_rfqs(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        wizard = self.env["mrp.workorder.assign.subcontract"].create(
            {
                "workorder_ids": [(6, 0, workorder.ids)],
                "partner_ids": [(6, 0, (self.partner | self.other_partner).ids)],
                "date_finished": self.fixed_date,
                "flow_type": "standard",
                "create_purchase_order": True,
                "type_id": self.po_type.id,
                "service_id": self.service.id,
            }
        )

        wizard.assign()

        purchase_orders = workorder.purchase_order_line_ids.order_id
        self.assertEqual(len(purchase_orders), 2)
        self.assertEqual(
            set(purchase_orders.mapped("partner_id").ids),
            set((self.partner | self.other_partner).ids),
        )
        self.assertEqual(
            set(workorder.purchase_order_line_ids.mapped("product_qty")), {10.0}
        )
        self.assertEqual(workorder.subcontract_state, "bidding")
