# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestBomTag(TransactionCase):
    def setUp(self):
        super(TestBomTag, self).setUp()
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

    def test_02_name_get(self):
        name_get_simple = self.bomtag.name_get()
        name_get_complete = self.bomtag.with_context(
            display_complete_name=True
        ).name_get()
        self.assertEqual(name_get_simple[0][1], "Furniture")
        self.assertEqual(name_get_complete[0][1], "Handmade / Furniture")
