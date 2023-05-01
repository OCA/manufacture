# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError
from odoo.tests import Form

from odoo.addons.mrp_subcontracting.tests.common import TestMrpSubcontractingCommon


class TestMrpSubcontractingSkipNoNegative(TestMrpSubcontractingCommon):
    def test_mrp_subcontracting_skip_no_negative(self):
        picking_form = Form(self.env["stock.picking"])
        picking_form.picking_type_id = self.env.ref("stock.picking_type_in")
        picking_form.partner_id = self.subcontractor_partner1
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = self.finished
            move.product_uom_qty = 1
        subcontracting_receipt = picking_form.save()
        subcontracting_receipt = subcontracting_receipt.with_context(
            test_stock_no_negative=True
        )
        subcontracting_receipt.action_confirm()
        self.assertEqual(subcontracting_receipt.state, "assigned")
        immediate_wizard = subcontracting_receipt.button_validate()
        self.assertEqual(immediate_wizard.get("res_model"), "stock.immediate.transfer")
        immediate_wizard_form = Form(
            self.env[immediate_wizard["res_model"]].with_context(
                **immediate_wizard["context"]
            )
        ).save()
        with self.assertRaises(ValidationError):
            immediate_wizard_form.process()

        # Create component stock, and subcontracting receipt should now be successful.
        self.env["stock.quant"].create(
            {
                "product_id": self.comp1.id,
                "location_id": self.subcontractor_partner1.property_stock_subcontractor.id,
                "quantity": 10,
            }
        )
        self.env["stock.quant"].create(
            {
                "product_id": self.comp2.id,
                "location_id": self.subcontractor_partner1.property_stock_subcontractor.id,
                "quantity": 10,
            }
        )
        immediate_wizard_form.process()
        self.assertEqual(subcontracting_receipt.state, "done")
