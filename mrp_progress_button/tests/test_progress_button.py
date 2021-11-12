# Copyright (C) 2017 Akretion (http://www.akretion.com). All Rights Reserved
# @author Florian DA COSTA <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProgressButton(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestProgressButton, self).setUp(*args, **kwargs)
        self.production_model = self.env["mrp.production"]
        self.bom_model = self.env["mrp.bom"]
        self.stock_location_stock = self.env.ref("stock.stock_location_stock")
        self.manufacture_route = self.env.ref("mrp.route_warehouse0_manufacture")
        self.uom_unit = self.env.ref("uom.product_uom_unit")

        self.product_manuf = self.env["product.product"].create(
            {
                "name": "Manuf",
                "type": "product",
                "uom_id": self.uom_unit.id,
                "route_ids": [(4, self.manufacture_route.id)],
            }
        )
        self.product_raw_material = self.env["product.product"].create(
            {
                "name": "Raw Material",
                "type": "product",
                "uom_id": self.uom_unit.id,
            }
        )

        self._update_product_qty(
            self.product_raw_material, self.stock_location_stock, 1
        )

        self.bom = self.env["mrp.bom"].create(
            {
                "product_id": self.product_manuf.id,
                "product_tmpl_id": self.product_manuf.product_tmpl_id.id,
                "bom_line_ids": (
                    [
                        (
                            0,
                            0,
                            {
                                "product_id": self.product_raw_material.id,
                                "product_qty": 1,
                                "product_uom_id": self.uom_unit.id,
                            },
                        ),
                    ]
                ),
            }
        )

    def _update_product_qty(self, product, location, quantity):
        """Update Product quantity."""
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Test Inventory",
                "product_ids": [(6, 0, product.ids)],
                "state": "confirm",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_qty": quantity,
                            "location_id": location.id,
                            "product_id": product.id,
                            "product_uom_id": product.uom_id.id,
                        },
                    )
                ],
            }
        )
        inventory.action_start()
        inventory.line_ids[0].write({"product_qty": quantity})
        inventory.action_validate()
        return quantity

    def test_manufacture_with_forecast_stock(self):
        """
        Test Manufacture mto with stock based on forecast quantity
        and no link between sub assemblies MO's and Main MO raw material
        """
        production = self.production_model.create(
            {
                "product_id": self.product_manuf.id,
                "product_qty": 1,
                "product_uom_id": self.uom_unit.id,
                "bom_id": self.bom.id,
            }
        )
        production.action_progress()
        self.assertEqual(production.state, "progress")
        production.action_unstart()
        self.assertEqual(production.state, "confirmed")
