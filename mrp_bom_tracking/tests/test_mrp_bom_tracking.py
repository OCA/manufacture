# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# - Lois Rilo <lois.rilo@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestBomTracking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_obj = cls.env["product.product"]
        cls.bom_obj = cls.env["mrp.bom"]
        cls.bom_line_obj = cls.env["mrp.bom.line"]

        # Create products:
        cls.product_1 = cls.product_obj.create([{"name": "TEST 01", "type": "consu"}])
        cls.component_1 = cls.product_obj.create([{"name": "RM 01", "type": "consu"}])
        cls.component_2 = cls.product_obj.create([{"name": "RM 02", "type": "consu"}])
        # cls.uom_1 = cls.env['uom.uom'].create({"name": "RM UOM", "category_id": 1})
        cls.component_2_alt = cls.product_obj.create(
            [{"name": "RM 02-B", "type": "consu"}]
        )

        # Create Bills of Materials:
        cls.bom = cls.bom_obj.create(
            [{"product_tmpl_id": cls.product_1.product_tmpl_id.id}]
        )
        cls.line_1 = cls.bom_line_obj.create(
            [
                {
                    "product_id": cls.component_1.id,
                    "bom_id": cls.bom.id,
                    "product_qty": 2.0,
                }
            ]
        )
        cls.line_2 = cls.bom_line_obj.create(
            [
                {
                    "product_id": cls.component_2.id,
                    "bom_id": cls.bom.id,
                    "product_qty": 5.0,
                }
            ]
        )

    def test_01_change_bom_lines(self):
        self.component_3 = self.product_obj.create([{"name": "RM 03", "type": "consu"}])
        bom_line_ids = self.bom_line_obj.create(
            [
                {
                    "product_id": self.component_3.id,
                    "product_qty": 2.0,
                    "bom_id": self.bom.id,
                }
            ]
        )
        self.bom.write({"bom_line_ids": [(6, 0, bom_line_ids.ids)]})

    def test_01_change_bom_line_qty(self):
        before = self.bom.message_ids
        self.line_2.write({"product_qty": 3.0})
        after = self.bom.message_ids
        self.assertEqual(len(after - before), 1)

    def test_02_change_bom_line_product(self):
        before = self.bom.message_ids
        self.line_2.write({"product_id": self.component_2_alt.id})
        after = self.bom.message_ids
        self.assertEqual(len(after - before), 1)
        self.line_2.write({"product_uom_id": 2})
