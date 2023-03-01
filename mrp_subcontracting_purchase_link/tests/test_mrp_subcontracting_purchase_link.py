# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields
from odoo.tests import tagged

from ...mrp_subcontracting.tests.common import TestMrpSubcontractingCommon


@tagged("post_install", "-at_install")
class TestMrpSubcontractingPurchaseLink(TestMrpSubcontractingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def _create_sub_po(self, products):
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.subcontractor_partner1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_qty": 5.0,
                            "product_uom": product.uom_id.id,
                            "price_unit": 10,
                            "date_planned": fields.Datetime.now(),
                        },
                    )
                    for product in products
                ],
            }
        )
        po.button_confirm()
        return po

    def test_01_prepare_subcontract_mo_vals(self):
        purchase_order = self._create_sub_po(self.finished)
        for picking in purchase_order.picking_ids:
            for move in picking.move_lines:
                self.assertEqual(
                    picking._prepare_subcontract_mo_vals(
                        move, move._get_subcontract_bom()
                    )["purchase_line_id"],
                    purchase_order.order_line.id,
                )

    def test_02_compute_subcontract_production_count(self):
        purchase_order1 = self._create_sub_po(self.finished)
        purchase_order2 = self._create_sub_po(self.finished + self.finished)
        self.assertEqual(purchase_order1.subcontract_production_count, 1)
        self.assertEqual(purchase_order2.subcontract_production_count, 2)

    def test_03_action_view_mrp(self):
        purchase_order1 = self._create_sub_po(self.finished)
        purchase_order2 = self._create_sub_po(self.finished + self.finished)
        action = purchase_order1.action_view_mrp()
        self.assertEqual(
            action["views"], [(self.env.ref("mrp.mrp_production_form_view").id, "form")]
        )
        self.assertEqual(
            action["res_id"],
            purchase_order1.subcontract_production_ids[0].id,
        )
        action = purchase_order2.action_view_mrp()
        self.assertEqual(
            action["domain"],
            [("id", "in", purchase_order2.subcontract_production_ids.ids)],
        )
