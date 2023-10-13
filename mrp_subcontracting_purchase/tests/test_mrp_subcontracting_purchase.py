from odoo.tests import Form

from odoo.addons.mrp_subcontracting.tests.common import TestMrpSubcontractingCommon


class MrpSubcontractingPurchaseTest(TestMrpSubcontractingCommon):
    def setUp(self):
        super().setUp()
        if "purchase.order" not in self.env:
            self.skipTest("`purchase` is not installed")

        self.finished2, self.comp3 = self.env["product.product"].create(
            [
                {
                    "name": "SuperProduct",
                    "type": "product",
                },
                {
                    "name": "Component",
                    "type": "consu",
                },
            ]
        )

        self.bom_finished2 = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.finished2.product_tmpl_id.id,
                "type": "subcontract",
                "subcontractor_ids": [(6, 0, self.subcontractor_partner1.ids)],
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.comp3.id,
                            "product_qty": 1,
                        },
                    )
                ],
            }
        )

    def test_count_smart_buttons(self):
        resupply_sub_on_order_route = self.env["stock.location.route"].search(
            [("name", "=", "Resupply Subcontractor on Order")]
        )
        (self.comp1 + self.comp2).write(
            {"route_ids": [4, (resupply_sub_on_order_route.id)]}
        )

        # I create a draft Purchase Order for first in move for 10 kg at 50 euro
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.subcontractor_partner1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "finished",
                            "product_id": self.finished.id,
                            "product_qty": 1.0,
                            "product_uom": self.finished.uom_id.id,
                            "price_unit": 50.0,
                        },
                    )
                ],
            }
        )

        po.button_confirm()

        self.assertEqual(po.subcontracting_resupply_picking_count, 1, "Must be equal 1")
        action1 = po.action_view_subcontracting_resupply()
        picking = self.env[action1["res_model"]].browse(action1["res_id"])
        self.assertEqual(
            picking.subcontracting_source_purchase_count, 1, "Must be equal 1"
        )
        action2 = picking.action_view_subcontracting_source_purchase()
        po_action2 = self.env[action2["res_model"]].browse(action2["res_id"])
        self.assertEqual(po_action2, po, "Should be equal")

    def test_purchase_and_return01(self):
        """
        The user buys 10 x a subcontracted product P. He receives the 10
        products and then does a return with 3 x P. The test ensures that the
        final received quantity is correctly computed
        """
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.subcontractor_partner1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.finished2.name,
                            "product_id": self.finished2.id,
                            "product_uom_qty": 10,
                            "product_uom": self.finished2.uom_id.id,
                            "price_unit": 1,
                        },
                    )
                ],
            }
        )
        po.button_confirm()

        mo = self.env["mrp.production"].search([("bom_id", "=", self.bom_finished2.id)])
        self.assertTrue(mo, "Must be equal 'True'")

        receipt = po.picking_ids
        receipt.move_lines.quantity_done = 10
        receipt.button_validate()

        return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_id=receipt.id, active_model="stock.picking"
            )
        )
        with return_form.product_return_moves.edit(0) as line:
            line.quantity = 3
            line.to_refund = True
        return_wizard = return_form.save()
        return_id, _ = return_wizard._create_returns()

        return_picking = self.env["stock.picking"].browse(return_id)
        return_picking.move_lines.quantity_done = 3
        return_picking.button_validate()

        self.assertEqual(self.finished2.qty_available, 7.0, "Must be equal 7.0")
        self.assertEqual(po.order_line.qty_received, 7.0, "Must be equal 7.0")

    def test_purchase_and_return02(self):
        """
        The user buys 10 x a subcontracted product P. He receives the 10
        products and then does a return with 3 x P (with the flag to_refund
        disabled and the subcontracting location as return location). The test
        ensures that the final received quantity is correctly computed
        """
        grp_multi_loc = self.env.ref("stock.group_stock_multi_locations")
        self.env.user.write({"groups_id": [(4, grp_multi_loc.id)]})

        po = self.env["purchase.order"].create(
            {
                "partner_id": self.subcontractor_partner1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.finished2.name,
                            "product_id": self.finished2.id,
                            "product_uom_qty": 10,
                            "product_uom": self.finished2.uom_id.id,
                            "price_unit": 1,
                        },
                    )
                ],
            }
        )
        po.button_confirm()

        mo = self.env["mrp.production"].search([("bom_id", "=", self.bom_finished2.id)])
        self.assertTrue(mo, "Must be equal 'True'")

        receipt = po.picking_ids
        receipt.move_lines.quantity_done = 10
        receipt.button_validate()

        return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_id=receipt.id, active_model="stock.picking"
            )
        )
        return_form.location_id = self.env.company.subcontracting_location_id
        with return_form.product_return_moves.edit(0) as line:
            line.quantity = 3
            line.to_refund = False
        return_wizard = return_form.save()
        return_id, _ = return_wizard._create_returns()

        return_picking = self.env["stock.picking"].browse(return_id)
        return_picking.move_lines.quantity_done = 3
        return_picking.button_validate()

        self.assertEqual(self.finished2.qty_available, 7.0, "Must be equal 7.0")
        self.assertEqual(po.order_line.qty_received, 10.0, "Must be equal 10.0")
