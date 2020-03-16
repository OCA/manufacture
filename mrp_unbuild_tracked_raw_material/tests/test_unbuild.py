# Copyright (C) 2019 Akretion (http://www.akretion.com). All Rights Reserved
# @author David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

# from odoo.tests.common import TransactionCase
from odoo.addons.mrp.tests.common import TestMrpCommon


class TestUnbuildUnmanufacturedProduct(TestMrpCommon):
    def setUp(self, *args, **kwargs):
        self.company = self.env.ref("base.main_company")
        self.loc = self.env.ref("stock.stock_location_stock")
        super().setUp(*args, **kwargs)

    def create_data(self):
        prd_to_build = self.env["product.product"].create(
            {
                "name": "To unbuild",
                "type": "product",
                "allow_unbuild_purchased": True,
                "tracking": "lot",
            }
        )
        prd_to_use1 = self.env["product.product"].create(
            {"name": "component 1", "type": "product", "tracking": "lot"}
        )
        prd_to_use2 = self.env["product.product"].create(
            {"name": "component 2", "type": "product", "tracking": "none"}
        )
        bom = self.env["mrp.bom"].create(
            {
                "product_id": prd_to_build.id,
                "product_tmpl_id": prd_to_build.product_tmpl_id.id,
                "product_uom_id": self.uom_unit.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    (0, 0, {"product_id": prd_to_use2.id, "product_qty": 1}),
                    (0, 0, {"product_id": prd_to_use1.id, "product_qty": 2}),
                ],
            }
        )
        return (bom, prd_to_build, prd_to_use1, prd_to_use2)

    def test_unbuild(self):
        bom, prd_to_build, prd_to_use1, prd_to_use2 = self.create_data()
        lot = self.env["stock.production.lot"].create(
            {
                "name": "%s" % datetime.now(),
                "product_id": prd_to_build.id,
                "company_id": self.company.id,
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            prd_to_build, self.loc, 10, lot_id=lot
        )
        unbuild = self.env["mrp.unbuild"].create(
            {
                "product_id": prd_to_build.id,
                "bom_id": bom.id,
                "product_qty": 1.0,
                "lot_id": lot.id,
                "product_uom_id": self.uom_unit.id,
                "location_id": self.loc.id,
                "location_dest_id": self.loc.id,
            }
        )
        unbuild.action_validate()
        self._check_qty(9, prd_to_build)
        self._check_qty(2, prd_to_use1)
        self._check_qty(1, prd_to_use2)

    def _check_qty(self, qty, product):
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                product, self.loc, allow_negative=True
            ),
            qty,
            "You should have the {} product '{}' in stock".format(qty, product.name),
        )
