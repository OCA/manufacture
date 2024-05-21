# Copyright (C) 2017 Akretion (http://www.akretion.com). All Rights Reserved
# @author Florian DA COSTA <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMrpAutoAssign(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestMrpAutoAssign, self).setUp(*args, **kwargs)
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
                "type": "normal",
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
        product_qty = self.env["stock.quant"].create(
            {
                "location_id": location.id,
                "product_id": product.id,
                "quantity": quantity,
            }
        )
        return product_qty

    def test_01_manufacture_auto_assign(self):
        """Test if Manufacturing order is auto-assigned."""
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.product_manuf
        mo_form.bom_id = self.bom
        mo_form.product_qty = 1
        production = mo_form.save()
        production.action_confirm()
        self.assertEqual(production.reservation_state, "assigned")
