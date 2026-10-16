# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import TransactionCase


class TestMrpComponentNoConsumption(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create a product with skip_mo_consumption True
        cls.product_skip = cls.env["product.product"].create(
            {
                "name": "Product Skip",
                "type": "consu",
                "is_storable": True,
                "skip_mo_consumption": True,
                "standard_price": 10.0,
            }
        )

        # Create a product without skip_mo_consumption
        cls.product_normal = cls.env["product.product"].create(
            {
                "name": "Product Normal",
                "type": "consu",
                "is_storable": True,
                "skip_mo_consumption": False,
                "standard_price": 5.0,
            }
        )

        cls.manufactured_product = cls.env["product.product"].create(
            {
                "name": "Manufactured Product",
                "type": "consu",
                "is_storable": True,
                "skip_mo_consumption": False,
                "standard_price": 15.0,
            }
        )

        # Create a BOM for the manufacturing order
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.manufactured_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_skip.id,
                            "product_qty": 1.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_normal.id,
                            "product_qty": 1.0,
                        },
                    ),
                ],
            }
        )
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.quant_1 = cls.env["stock.quant"].create(
            {
                "product_id": cls.product_normal.id,
                "quantity": 5,
                "location_id": cls.warehouse.lot_stock_id.id,
            }
        )
        cls.quant_2 = cls.env["stock.quant"].create(
            {
                "product_id": cls.product_skip.id,
                "quantity": 5,
                "location_id": cls.warehouse.lot_stock_id.id,
            }
        )

    def test_post_inventory_skips_product(self):
        # Create a manufacturing order
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product_skip.id,
                "bom_id": self.bom.id,
                "product_qty": 1.0,
            }
        )
        mo.action_confirm()
        mo.move_raw_ids.write({"quantity": 1})
        mo.button_mark_done()

        # Check the created stock valuation layers
        for move in mo.move_raw_ids:
            if move.product_id.skip_mo_consumption:
                self.assertEqual(move.state, "done")
                qty = self.quant_2._get_available_quantity(
                    move.product_id, self.warehouse.lot_stock_id
                )
                self.assertEqual(qty, 5)
            else:
                self.assertEqual(move.state, "done")
                qty = self.quant_1._get_available_quantity(
                    move.product_id, self.warehouse.lot_stock_id
                )
                self.assertEqual(qty, 4)
