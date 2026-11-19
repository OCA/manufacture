# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import Form

from ...mrp_subcontracting.tests.common import TestMrpSubcontractingCommon


class TestMrpSubcontractingResupplyStatus(TestMrpSubcontractingCommon):
    def _create_subcontracting_po(self):
        po_form = Form(self.env["purchase.order"])
        po_form.partner_id = self.subcontractor_partner1
        with po_form.order_line.new() as line:
            line.product_id = self.finished
            line.product_qty = 1
            line.price_unit = 100.0
        po = po_form.save()
        po.button_confirm()
        return po

    def _validate(self, moves):
        for move in moves:
            move.quantity = move.product_uom_qty
            move.picked = True
        res = moves.picking_id.button_validate()
        if isinstance(res, dict):
            Form.from_action(self.env, res).save().process()

    def _assert_status(self, status, *records):
        for record in records:
            self.assertEqual(record.resupply_status, status, record.display_name)

    def test_resupply_status(self):
        po = self._create_subcontracting_po()
        other_po = self._create_subcontracting_po()
        receipt = po.picking_ids
        resupply = receipt._get_subcontracting_resupplies()
        self.assertEqual(len(resupply), 1)
        self.assertEqual(len(resupply.move_ids), 2)
        self._assert_status("pending", po, receipt, other_po, other_po.picking_ids)

        self._validate(resupply.move_ids[0])
        backorder = resupply.backorder_ids
        self.assertTrue(backorder)
        self.assertEqual(receipt._get_subcontracting_resupplies(), resupply + backorder)
        self._assert_status("partial", po, receipt)
        self._assert_status("pending", other_po, other_po.picking_ids)

        self._validate(backorder.move_ids)
        self._assert_status("full", po, receipt)
        self._assert_status("pending", other_po, other_po.picking_ids)

    def test_resupply_status_cancelled(self):
        po = self._create_subcontracting_po()
        po.picking_ids._get_subcontracting_resupplies().action_cancel()
        self._assert_status(False, po, po.picking_ids)

    def test_resupply_status_no_resupply(self):
        self.env.ref("stock.warehouse0").subcontracting_to_resupply = False
        po = self._create_subcontracting_po()
        self.assertFalse(po.picking_ids._get_subcontracting_resupplies())
        self._assert_status(False, po, po.picking_ids)
