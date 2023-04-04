# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields
from odoo.tests import tagged

from ...mrp_subcontracting.tests.common import TestMrpSubcontractingCommon


@tagged("post_install", "-at_install")
class TestMrpSubcontractingOwner(TestMrpSubcontractingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Owner
        cls.owner_id = cls.env["res.partner"].create({"name": "Owner test"})

    def _create_sub_po(self, products):
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.subcontractor_partner1.id,
                "owner_id": self.owner_id.id,
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

    def test_mrp_subcontracting_owner(self):
        purchase_order = self._create_sub_po(self.finished)
        for picking in purchase_order.picking_ids:
            for move in picking.move_ids:
                self.assertEqual(
                    picking._prepare_subcontract_mo_vals(
                        move, move._get_subcontract_bom()
                    )["owner_id"],
                    self.owner_id.id,
                )
