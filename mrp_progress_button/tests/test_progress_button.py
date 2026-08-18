# Copyright (C) 2017 Akretion (http://www.akretion.com). All Rights Reserved
# @author Florian DA COSTA <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestProgressButton(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.production_model = self.env["mrp.production"]
        self.bom_model = self.env["mrp.bom"]
        self.manufacture_route = self.env.ref("mrp.route_warehouse0_manufacture")
        self.uom_unit = self.env.ref("uom.product_uom_unit")

        self.product_manuf = self.env["product.product"].create(
            {
                "name": "Manuf",
                "type": "consu",
                "uom_id": self.uom_unit.id,
                "route_ids": [(4, self.manufacture_route.id)],
            }
        )
        self.product_raw_material = self.env["product.product"].create(
            {
                "name": "Raw Material",
                "type": "consu",
                "uom_id": self.uom_unit.id,
            }
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

    def test_01_manufacture_with_forecast_stock(self):
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
        production.action_confirm()
        production.action_start()
        self.assertEqual(production.state, "progress")
        self.assertEqual(
            production.date_start.replace(microsecond=0),
            fields.Datetime.now().replace(microsecond=0),
        )
        production.action_unstart()
        self.assertEqual(production.state, "confirmed")
