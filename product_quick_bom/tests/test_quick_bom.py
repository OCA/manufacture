#   Copyright (C) 2015 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestQuickBom(TransactionCase):
    def setUp(self):
        # as we test new BoMs that must not already exist in demo data,
        # bolt + screw + ply = lamp
        super().setUp()
        self.prd_1 = self.env.ref("mrp.product_product_computer_desk_bolt")
        self.prd_2 = self.env.ref("mrp.product_product_computer_desk_screw")
        self.prd_3 = self.env.ref("mrp.product_product_wood_ply")
        self.tmpl_4 = self.env.ref("product.product_delivery_02_product_template")

    def test_create_bom(self):
        self.tmpl_4.button_create_bom()
        self.tmpl_4.write(
            {
                "specific_bom_line_ids": [
                    (0, 0, {"product_id": self.prd_1.id, "product_qty": 2}),
                    (0, 0, {"product_id": self.prd_2.id, "product_qty": 2}),
                    (0, 0, {"product_id": self.prd_3.id, "product_qty": 1}),
                ]
            }
        )
        bom = self.tmpl_4.bom_id
        self.assertEqual(self.tmpl_4.id, bom.product_tmpl_id.id)
        self.assertEqual(bom.bom_line_ids[0].product_id.id, self.prd_1.id)
        self.assertEqual(bom.bom_line_ids[0].product_qty, 2)
        self.assertEqual(bom.bom_line_ids[1].product_id.id, self.prd_2.id)
        self.assertEqual(bom.bom_line_ids[1].product_qty, 2)
        self.assertEqual(bom.bom_line_ids[2].product_id.id, self.prd_3.id)
        self.assertEqual(bom.bom_line_ids[2].product_qty, 1)

    def test_read_bom(self):
        bom = self.env["mrp.bom"].create(
            {"type": "normal", "product_tmpl_id": self.tmpl_4.id}
        )
        bomline1 = self.env["mrp.bom.line"].create(
            {"product_id": self.prd_1.id, "product_qty": 2, "bom_id": bom.id}
        )
        bomline2 = self.env["mrp.bom.line"].create(
            {"product_id": self.prd_2.id, "product_qty": 2, "bom_id": bom.id}
        )
        bomline3 = self.env["mrp.bom.line"].create(
            {"product_id": self.prd_3.id, "product_qty": 1, "bom_id": bom.id}
        )
        self.assertTrue(bomline1 in self.tmpl_4.specific_bom_line_ids)
        self.assertTrue(bomline2 in self.tmpl_4.specific_bom_line_ids)
        self.assertTrue(bomline3 in self.tmpl_4.specific_bom_line_ids)
