# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestBomTag(TransactionCase):
    def setUp(self):
        super().setUp()
        self.bomtag = self.env.ref("mrp_bom_tag.demo_bom_tag")
        self.bomtag2 = self.env.ref("mrp_bom_tag.demo_bom_tag_2")
        self.bomtagparent = self.env.ref("mrp_bom_tag.demo_bom_tag_parent")
        self.bom_desk = self.env.ref("mrp.mrp_bom_manufacture")

    def test_01_bom_qty(self):
        self.assertEqual(
            self.bomtag2.bom_qty,
            0,
        )
        self.bom_desk.write(
            {
                "bom_tag_ids": [
                    (6, 0, [self.bomtag2.id]),
                ]
            }
        )
        self.assertEqual(
            self.bomtag2.bom_qty,
            1,
        )

    def test_02_display_name(self):
        self.assertEqual(self.bomtag.display_name, "Furniture")
        self.assertEqual(
            self.bomtag.with_context(display_complete_name=True).display_name,
            "Handmade / Furniture",
        )
