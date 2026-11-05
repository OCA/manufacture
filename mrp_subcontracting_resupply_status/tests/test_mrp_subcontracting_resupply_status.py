# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import Form

from ...mrp_subcontracting.tests.common import TestMrpSubcontractingCommon


class TestMrpSubcontractingResupplyStatus(TestMrpSubcontractingCommon):
    def setUp(self):
        super().setUp()
        self.resupply_route = self.env.ref(
            "mrp_subcontracting.route_resupply_subcontractor_mto"
        )
        self.comp1.route_ids = [(6, 0, [self.resupply_route.id])]
        self.comp2.route_ids = [(6, 0, [self.resupply_route.id])]
        self.po = self._create_subcontracting_po()

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

    def test_purchase_order_resupply_status(self):
        (self.comp1 + self.comp2).write({"route_ids": [(4, self.resupply_route.id)]})
        po = self.po

        resupply = po._get_subcontracting_resupplies()
        self.assertTrue(resupply)
        # Force to have two resupplies
        resupply.copy()
        resupplies = po._get_subcontracting_resupplies()
        self.assertEqual(len(resupplies), 2)

        self.assertEqual(po.resupply_status, "pending")

        partial = resupplies[:1]
        for picking in partial:
            picking.action_confirm()
            for move in picking.move_ids:
                move._set_quantity_done(move.product_uom_qty)
            picking.button_validate()

        self.assertEqual(po.resupply_status, "partial")

        for picking in resupplies:
            if picking.state != "done":
                picking.action_confirm()
                for move in picking.move_ids:
                    move._set_quantity_done(move.product_uom_qty)
                picking.button_validate()

        self.assertEqual(po.resupply_status, "full")

    def test_stock_picking_resupply_status(self):
        (self.comp1 + self.comp2).write({"route_ids": [(4, self.resupply_route.id)]})
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

        self.assertEqual(receipt.resupply_status, "pending")

        partial = resupplies[:1]
        for picking in partial:
            picking.action_confirm()
            for move in picking.move_ids:
                move._set_quantity_done(move.product_uom_qty)
            picking.button_validate()

        self.assertEqual(receipt.resupply_status, "partial")

        for picking in resupplies:
            if picking.state != "done":
                picking.action_confirm()
                for move in picking.move_ids:
                    move._set_quantity_done(move.product_uom_qty)
                picking.button_validate()

        self.assertEqual(receipt.resupply_status, "full")

    def test_resupply_status_no_resupply(self):
        self.comp1.route_ids = [(6, 0, [])]
        self.comp2.route_ids = [(6, 0, [])]
        po = self._create_subcontracting_po()
        self.assertEqual(po.resupply_status, False)

        receipt = po.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "incoming"
        )
        self.assertEqual(receipt.resupply_status, False)
