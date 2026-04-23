from odoo.tests import tagged

from .common import WorkorderSubcontractingCommon


@tagged("post_install", "-at_install")
class TestSubcontractingTraceabilityUi(WorkorderSubcontractingCommon):
    def test_01_purchase_order_action_opens_linked_workorders(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        purchase_order = self._assign_standard_purchase_order(workorder)

        action = purchase_order.action_view_subcontract_workorders()

        self.assertEqual(action["res_model"], "mrp.workorder")
        self.assertEqual(action["view_mode"], "list,form")
        self.assertEqual(action["domain"], [("id", "in", workorder.ids)])
        self.assertEqual(purchase_order.subcontract_workorder_count, 1)

    def test_02_picking_action_opens_linked_workorders(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        self._confirm_standard_purchase_order(workorder)
        picking = workorder.delivery_move_ids.picking_id

        action = picking.action_view_subcontract_workorders()

        self.assertEqual(action["res_model"], "mrp.workorder")
        self.assertEqual(action["view_mode"], "list,form")
        self.assertEqual(action["domain"], [("id", "in", workorder.ids)])
        self.assertEqual(picking.sub_workorder_count, 1)

    def test_03_stock_move_action_opens_own_picking(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        self._confirm_standard_purchase_order(workorder)
        move = workorder.delivery_move_ids

        action = move.action_open_subcontract_picking()

        self.assertEqual(action["res_model"], "stock.picking")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["res_id"], move.picking_id.id)

    def test_04_navigation_fields_are_computed_on_subcontract_moves(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        self._confirm_standard_purchase_order(workorder)
        move = workorder.delivery_move_ids

        self.assertEqual(move.sub_workorder_id, workorder)
        self.assertEqual(move.sub_production_id, workorder.production_id)
        self.assertEqual(move.subcontracting_flow, "parts")
