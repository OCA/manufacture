# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestMrpBomLineSequence(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Product = cls.env["product.product"]
        cls.product = cls.Product.create({"name": "Finished", "is_storable": True})
        cls.components = cls.Product.create(
            [{"name": f"Component {i}", "is_storable": True} for i in range(4)]
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_qty": 1.0,
                "bom_line_ids": [
                    Command.create({"product_id": component.id, "product_qty": 1.0})
                    for component in cls.components[:3]
                ],
            }
        )

    def test_create_numbers_lines(self):
        self.assertEqual(self.bom.bom_line_ids.mapped("sequence"), [1, 2, 3])
        self.assertEqual(self.bom.bom_line_ids.mapped("sequence2"), [1, 2, 3])
        self.assertEqual(self.bom.bom_line_ids.product_id.ids, self.components[:3].ids)

    def test_new_line_added_at_the_end(self):
        line = self.env["mrp.bom.line"].create(
            {
                "bom_id": self.bom.id,
                "product_id": self.components[3].id,
                "product_qty": 1.0,
            }
        )
        self.assertEqual(line.sequence, 4)
        self.assertEqual(self.bom.bom_line_ids.mapped("sequence"), [1, 2, 3, 4])

    def test_new_line_with_explicit_sequence(self):
        line = self.env["mrp.bom.line"].create(
            {
                "bom_id": self.bom.id,
                "product_id": self.components[3].id,
                "product_qty": 1.0,
                "sequence": 0,
            }
        )
        self.assertEqual(line.sequence, 1)
        self.assertEqual(
            self.bom.bom_line_ids.sorted("sequence").product_id.ids,
            (self.components[3] | self.components[:3]).ids,
        )

    def test_copy_keeps_sequence(self):
        self.bom.bom_line_ids[0].sequence = 10
        new_bom = self.bom.copy()
        self.assertEqual(
            new_bom.bom_line_ids.sorted("sequence").mapped(
                lambda bl: (bl.sequence, bl.product_id.id)
            ),
            [
                (2, self.components[1].id),
                (3, self.components[2].id),
                (10, self.components[0].id),
            ],
        )

    def test_edit_visible_sequence(self):
        line = self.bom.bom_line_ids[2]
        line.sequence2 = 0
        self.assertEqual(line.sequence, 0)
        self.bom.invalidate_recordset(["bom_line_ids"])
        self.assertEqual(self.bom.bom_line_ids[:1], line)
