# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# - Lois Rilo <lois.rilo@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestBomTracking(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_obj = cls.env["product.product"]
        cls.bom_obj = cls.env["mrp.bom"]
        cls.bom_line_obj = cls.env["mrp.bom.line"]
        cls.product_uom_category_obj = cls.env["uom.category"]
        cls.product_uom_obj = cls.env["uom.uom"]

         # Create uom category:
        cls.product_uom_category_obj_1 = cls.product_uom_category_obj.create({"name": "weight"})
        
        # Create uoms:
        cls.product_uom_obj_1 = cls.product_uom_obj.create({"name": "kg", "category_id": cls.product_uom_category_obj_1.id})
        cls.product_uom_obj_2 = cls.product_uom_obj.create({"name": "g", "category_id": cls.product_uom_category_obj_1.id, "uom_type": "smaller", "factor": 1000, "rounding": 1})
         
        # Create products:
        cls.product_1 = cls.product_obj.create({"name": "TEST 01", "type": "product"})
        cls.component_1 = cls.product_obj.create({"name": "RM 01", "type": "product"})
        cls.component_2 = cls.product_obj.create({"name": "RM 02", "type": "product"})
        cls.component_3 = cls.product_obj.create({"name": "RM 03", "type": "product", "uom_id": cls.product_uom_obj_1.id})
        cls.component_2_alt = cls.product_obj.create(
            {"name": "RM 02-B", "type": "product"}
        )

        # Create Bills of Materials:
        cls.bom = cls.bom_obj.create(
            {"product_tmpl_id": cls.product_1.product_tmpl_id.id}
        )
        cls.line_1 = cls.bom_line_obj.create(
            {"product_id": cls.component_1.id, "bom_id": cls.bom.id, "product_qty": 2.0}
        )
        cls.line_2 = cls.bom_line_obj.create(
            {"product_id": cls.component_2.id, "bom_id": cls.bom.id, "product_qty": 5.0}
        )
        cls.line_3 = cls.bom_line_obj.create(
            {"product_id": cls.component_3.id, "bom_id": cls.bom.id, "product_qty": 10.0, "product_uom_id": cls.product_uom_obj_1.id}
        )

    def test_01_change_bom_line_qty(self):
        before = self.bom.message_ids
        self.line_1.product_qty = 3.0
        after = self.bom.message_ids
        self.assertEqual(len(after - before), 1)

    def test_02_change_bom_line_product(self):
        before = self.bom.message_ids
        self.line_2.product_id = self.component_2_alt
        after = self.bom.message_ids
        self.assertEqual(len(after - before), 1)
        
    def test_03_change_bom_line_product_uom(self):
        before = self.bom.message_ids
        self.line_3.product_uom_id = self.product_uom_obj_2.id
        after = self.bom.message_ids
        self.assertEqual(len(after - before), 1)
