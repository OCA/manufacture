# © 2018 Agung Rachmatullah
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMrpBomNote(TransactionCase):
    def setUp(self):
        super(TestMrpBomNote, self).setUp()
        self.product_t = self.env["product.template"]
        self.product_p = self.env["product.product"]
        self.bom = self.env["mrp.bom"]

    def test_notes(self):
        uom_unit = self.env.ref("uom.product_uom_unit")
        product_t_fg = self.product_t.create(
            {
                "name": "Chair",
                "type": "product",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
            }
        )
        product_t_1 = self.product_t.create(
            {
                "name": "Log 1",
                "type": "product",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
            }
        )
        product_t_2 = self.product_t.create(
            {
                "name": "Log 2",
                "type": "product",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
            }
        )
        product_t_3 = self.product_t.create(
            {
                "name": "Log 3",
                "type": "product",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
            }
        )
        product_fg = self.product_p.create({"product_tmpl_id": product_t_fg.id})
        product_1 = self.product_p.create({"product_tmpl_id": product_t_1.id})
        product_2 = self.product_p.create({"product_tmpl_id": product_t_2.id})
        product_3 = self.product_p.create({"product_tmpl_id": product_t_3.id})
        BoM1 = self.bom.create(
            {
                "product_id": product_fg.id,
                "product_tmpl_id": product_fg.product_tmpl_id.id,
                "product_uom_id": uom_unit.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    (0, 0, {"product_id": product_1.id, "product_qty": 4}),
                    (0, 0, {"product_id": product_2.id, "product_qty": 2}),
                    (0, 0, {"product_id": product_3.id, "product_qty": 2}),
                ],
            }
        )

        BoM1.write({"notes": "<p>Test</p>"})
        self.assertEqual(BoM1.notes, "<p>Test</p>")
