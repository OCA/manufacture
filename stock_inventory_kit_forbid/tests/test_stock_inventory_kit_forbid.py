# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.tests import Form, common


class TestStockWholeKitConstraint(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.product_kit_1 = cls.env["product.product"].create(
            {"name": "Product Kit 1", "type": "product"}
        )
        cls.component_1_kit_1 = cls.env["product.product"].create(
            {"name": "Component 1 Kit 1", "type": "product"}
        )
        cls.component_2_kit_1 = cls.env["product.product"].create(
            {"name": "Component 2 Kit 1", "type": "product"}
        )
        bom_form = Form(cls.env["mrp.bom"])
        bom_form.product_tmpl_id = cls.product_kit_1.product_tmpl_id
        bom_form.product_id = cls.product_kit_1
        bom_form.type = "phantom"
        with bom_form.bom_line_ids.new() as line:
            line.product_id = cls.component_1_kit_1
        with bom_form.bom_line_ids.new() as line:
            line.product_id = cls.component_2_kit_1
        cls.bom_kit_1 = bom_form.save()

    def test_01_inventory_not_allowed(self):
        """Test inventory adjustment not allowed for kits unless it is set in the
        product template"""
        inv_line_data = {
            "product_id": self.product_kit_1.id,
            "product_uom_id": self.product_kit_1.uom_id.id,
            "product_qty": 1,
            "location_id": self.stock_location.id,
        }
        with self.assertRaises(ValidationError):
            self.env["stock.inventory"].create(
                {
                    "name": "I have no idea what I am doing",
                    "line_ids": [(0, 0, dict(inv_line_data))],
                }
            )
        # test not error is raised if the check is set in the template
        self.product_kit_1.allow_kit_inventory = True
        self.env["stock.inventory"].create(
            {"name": "I am doing well", "line_ids": [(0, 0, dict(inv_line_data))]}
        )
