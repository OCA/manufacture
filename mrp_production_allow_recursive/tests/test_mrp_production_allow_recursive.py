# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestMrpProductionAllowRecursive(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["product.category"].create({"name": "Test Category"})
        cls.product_finished = cls.env["product.product"].create(
            {"name": "Finished Product"}
        )
        cls.product_component = cls.env["product.product"].create(
            {"name": "Component Product"}
        )

    def test_mrp_production_allow_recursive(self):
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product_finished.id,
                "product_qty": 1.0,
            }
        )
        mo.write(
            {
                "move_raw_ids": [
                    Command.create(
                        {
                            "product_id": self.product_component.id,
                            "product_uom_qty": 1.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_finished.id,
                            "product_uom_qty": 1.0,
                        }
                    ),
                ]
            }
        )
        result = mo._onchange_product_id()
        self.assertIn(
            "warning", result, "No warning was returned by the onchange method."
        )

        mo.company_id.allow_same_product_component_finish = True
        result = mo._onchange_product_id()
        self.assertIsNone(result, "Unexpected result returned by onchange.")
