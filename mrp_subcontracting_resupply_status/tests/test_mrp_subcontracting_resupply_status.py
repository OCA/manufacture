# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import Form

from ...mrp_subcontracting.tests.common import TestMrpSubcontractingCommon


class TestMrpSubcontractingResupplyStatus(TestMrpSubcontractingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        resupply_route = cls.env.ref(
            "mrp_subcontracting.route_resupply_subcontractor_mto"
        )
        cls.comp1.route_ids = [(6, 0, [resupply_route.id])]
        cls.comp2.route_ids = [(6, 0, [resupply_route.id])]
        cls.po = cls._create_subcontracting_po()

    @classmethod
    def _create_subcontracting_po(cls):
        po_form = Form(cls.env["purchase.order"])
        po_form.partner_id = cls.subcontractor_partner1
        with po_form.order_line.new() as line:
            line.product_id = cls.finished
            line.product_qty = 1
            line.product_uom = cls.finished.uom_id
            line.price_unit = 100.0
        po = po_form.save()
        po.button_confirm()
        return po

    def test_purchase_order_resupply_status(self):
        po = self.po

        resupply = po._get_subcontracting_resupplies()
        self.assertTrue(resupply)
        # Force to have two resupplies
        resupply.copy()
        resupplies = po._get_subcontracting_resupplies()
        self.assertEqual(len(resupplies), 2)

        po._compute_resupply_status()
        self.assertEqual(po.resupply_status, "pending")

        partial = resupplies[:1]
        for picking in partial:
            picking.action_confirm()
            for move in picking.move_ids:
                move.quantity_done = move.product_uom_qty
            picking.button_validate()

        po._compute_resupply_status()
        self.assertEqual(po.resupply_status, "partial")

        for picking in resupplies:
            if picking.state != "done":
                picking.action_confirm()
                for move in picking.move_ids:
                    move.quantity_done = move.product_uom_qty
                picking.button_validate()

        po._compute_resupply_status()
        self.assertEqual(po.resupply_status, "full")

    def test_stock_picking_resupply_status(self):
        receipt = self.po.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "incoming"
        )
        self.assertTrue(receipt)
        receipt = receipt[0]

        resupply = receipt._get_subcontracting_resupplies()
        self.assertTrue(resupply)

        # Force to have two resupplies
        resupply.copy()
        resupplies = receipt._get_subcontracting_resupplies()
        self.assertEqual(len(resupplies), 2)

        receipt._compute_resupply_status()
        self.assertEqual(receipt.resupply_status, "pending")

        partial = resupplies[:1]
        for picking in partial:
            picking.action_confirm()
            for move in picking.move_ids:
                move.quantity_done = move.product_uom_qty
            picking.button_validate()

        receipt._compute_resupply_status()
        self.assertEqual(receipt.resupply_status, "partial")

        for picking in resupplies:
            if picking.state != "done":
                picking.action_confirm()
                for move in picking.move_ids:
                    move.quantity_done = move.product_uom_qty
                picking.button_validate()

        receipt._compute_resupply_status()
        self.assertEqual(receipt.resupply_status, "full")

    def test_resupply_status_no_resupply(self):
        self.comp1.route_ids = [(6, 0, [])]
        self.comp2.route_ids = [(6, 0, [])]
        po = self._create_subcontracting_po()
        po._compute_resupply_status()
        self.assertEqual(po.resupply_status, False)

        receipt = po.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "incoming"
        )
        receipt._compute_resupply_status()
        self.assertEqual(receipt.resupply_status, False)
