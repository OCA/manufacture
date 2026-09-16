# Copyright 2023 Quartile Limited
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import Form
from odoo.tools import mute_logger

from odoo.addons.mrp_subcontracting.tests.common import TestMrpSubcontractingCommon


class TestMrpSubcontractingSkipNoNegative(TestMrpSubcontractingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_stock_no_negative=True,
            )
        )
        picking_form = Form(cls.env["stock.picking"])
        picking_form.picking_type_id = cls.env.ref("stock.picking_type_in")
        picking_form.partner_id = cls.subcontractor_partner1
        picking_form.picking_type_id.auto_show_reception_report = True
        cls.env.user.groups_id += cls.env.ref("stock.group_reception_report")
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = cls.finished
            move.product_id.type = "product"
            move.product_uom_qty = 1
        cls.subcontracting_receipt = picking_form.save()
        type_id = picking_form.picking_type_id
        cls.move = cls.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": cls.finished.id,
                "product_uom_qty": 10,
                "location_id": type_id.warehouse_id.view_location_id.id,
                "location_dest_id": type_id.warehouse_id.view_location_id.id,
                "move_orig_ids": False,
                "product_uom": cls.env.ref("uom.product_uom_unit").id,
                "state": "assigned",
            }
        )

    def _create_stock_quant(self, product, qty):
        partner1 = self.subcontractor_partner1
        self.env["stock.quant"].create(
            {
                "product_id": product.id,
                "location_id": partner1.property_stock_subcontractor.id,
                "quantity": qty,
            }
        )

    @mute_logger("odoo.models.unlink")
    def test_mrp_subcontracting_skip_no_negative_01(self):
        self._create_stock_quant(self.comp1, 10)
        self._create_stock_quant(self.comp2, 10)
        self.subcontracting_receipt.action_confirm()
        self.assertEqual(self.subcontracting_receipt.state, "assigned")
        immediate_wizard = self.subcontracting_receipt.sudo().button_validate()
        self.assertEqual(
            immediate_wizard.get("res_model"), "report.stock.report_reception"
        )
        immediate_wizard_form = self.env[immediate_wizard["res_model"]].with_context(
            **immediate_wizard["context"]
        )
        self.assertFalse(immediate_wizard_form)
        self.assertEqual(self.subcontracting_receipt.state, "done")

    def test_mrp_subcontracting_skip_no_negative_03(self):
        self._create_stock_quant(self.comp1, 10)
        self._create_stock_quant(self.comp2, 10)
        self.subcontracting_receipt.action_confirm()
        self.assertEqual(self.subcontracting_receipt.state, "assigned")
        immediate_wizard = self.subcontracting_receipt.sudo().button_validate()
        self.assertEqual(
            immediate_wizard.get("res_model"), "report.stock.report_reception"
        )
        immediate_wizard_form = self.env[immediate_wizard["res_model"]].with_context(
            **immediate_wizard["context"]
        )
        self.assertFalse(immediate_wizard_form)
        self.assertEqual(self.subcontracting_receipt.state, "done")

    def test_mrp_subcontracting_skip_no_negative_04(self):
        partner1 = self.subcontractor_partner1
        partner1.property_stock_subcontractor.allow_negative_stock = True
        self.subcontracting_receipt.action_confirm()
        self.assertEqual(self.subcontracting_receipt.state, "assigned")
        immediate_wizard = self.subcontracting_receipt.sudo().button_validate()
        self.assertEqual(
            immediate_wizard.get("res_model"), "report.stock.report_reception"
        )
        immediate_wizard_form = self.env[immediate_wizard["res_model"]].with_context(
            **immediate_wizard["context"]
        )
        self.assertFalse(immediate_wizard_form)
        self.assertEqual(self.subcontracting_receipt.state, "done")

    def test_mrp_subcontracting_with_normal_product(self):
        another_product = self.env["product.product"].create(
            {
                "name": "Another Product",
                "type": "product",
            }
        )
        self.env["stock.move"].create(
            {
                "picking_id": self.subcontracting_receipt.id,
                "product_id": another_product.id,
                "name": another_product.name,
                "product_uom": another_product.uom_id.id,
                "product_uom_qty": 1,
                "location_id": self.subcontracting_receipt.location_id.id,
                "location_dest_id": self.subcontracting_receipt.location_dest_id.id,
            }
        )
        self._create_stock_quant(self.comp1, 10)
        self._create_stock_quant(self.comp2, 10)
        self.subcontracting_receipt.action_confirm()
        self.assertEqual(self.subcontracting_receipt.state, "assigned")
        immediate_wizard = self.subcontracting_receipt.sudo().button_validate()
        self.assertEqual(
            immediate_wizard.get("res_model"), "report.stock.report_reception"
        )
        immediate_wizard_form = self.env[immediate_wizard["res_model"]].with_context(
            **immediate_wizard["context"]
        )
        self.assertFalse(immediate_wizard_form)
        self.assertEqual(self.subcontracting_receipt.state, "done")
        products = self.subcontracting_receipt.move_ids.mapped("product_id")
        self.assertIn(self.finished, products)
        self.assertIn(another_product, products)
        for move in self.subcontracting_receipt.move_ids:
            self.assertEqual(move.quantity, 1)

    def test_mrp_subcontracting_with_normal_product_backorder(self):
        """
        Mixed receipt: validate only the subcontract move, request a backorder.
        The normal move (qty_done=0) must be moved to a backorder picking.
        """
        another_product = self.env["product.product"].create(
            {
                "name": "Another Product",
                "type": "product",
            }
        )
        normal_move = self.env["stock.move"].create(
            {
                "picking_id": self.subcontracting_receipt.id,
                "product_id": another_product.id,
                "name": another_product.name,
                "product_uom": another_product.uom_id.id,
                "product_uom_qty": 1,
                "location_id": self.subcontracting_receipt.location_id.id,
                "location_dest_id": self.subcontracting_receipt.location_dest_id.id,
            }
        )
        self._create_stock_quant(self.comp1, 10)
        self._create_stock_quant(self.comp2, 10)
        self.subcontracting_receipt.action_confirm()
        self.assertEqual(self.subcontracting_receipt.state, "assigned")
        # Only set qty_done on the subcontract move; leave the normal move at 0.
        subcontract_move = self.subcontracting_receipt.move_ids.filtered(
            lambda m: m.is_subcontract
        )
        subcontract_move.quantity = 1
        subcontract_move.picked = True
        backorder_wizard = self.subcontracting_receipt.sudo().button_validate()
        self.assertEqual(
            backorder_wizard.get("res_model"), "stock.backorder.confirmation"
        )
        backorder_wizard_form = Form(
            self.env[backorder_wizard["res_model"]].with_context(
                **backorder_wizard["context"]
            )
        ).save()
        backorder_wizard_form.process()
        # The subcontract move is done on the original picking.
        self.assertEqual(subcontract_move.state, "done")
        self.assertEqual(subcontract_move.quantity, 1)
        # A backorder picking must have been created with the unprocessed
        # normal move; it must no longer be on the original picking.
        backorder = self.env["stock.picking"].search(
            [("backorder_id", "=", self.subcontracting_receipt.id)]
        )
        self.assertTrue(backorder)
        self.assertNotIn(normal_move, self.subcontracting_receipt.move_ids)
        self.assertIn(normal_move, backorder.move_ids)
        self.assertEqual(normal_move.product_uom_qty, 1)
