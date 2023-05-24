# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class MrpProductionCase(TransactionCase):
    def setUp(self):
        super(MrpProductionCase, self).setUp()
        self.product_model = self.env["product.product"]
        self.bom_model = self.env["mrp.bom"]
        self.route_model = self.env["stock.location.route"]
        self.loc_model = self.env["stock.location"]
        self.op_type_model = self.env["stock.picking.type"]

        self.wh = self.env.ref("stock.warehouse0")
        self.standard_manuf_route = self.env.ref("mrp.route_warehouse0_manufacture")
        self.standard_manuf_op_type = self.wh.manu_type_id

        self.product_1 = self.product_model.create(
            {"name": "Product 1", "route_ids": [(6, 0, self.standard_manuf_route.ids)]}
        )

        self.source_loc_2 = self.loc_model.create(
            {
                "name": "Pre Production 2",
                "location_id": self.wh.view_location_id.id,
                "usage": "internal",
            }
        )
        self.op_type_2 = self.op_type_model.create(
            {
                "name": "Secondary Manufacturing",
                "code": "mrp_operation",
                "sequence_code": "MO/SEC",
                "default_location_src_id": self.source_loc_2.id,
                "default_location_dest_id": self.wh.lot_stock_id.id,
            }
        )
        self.secondary_manuf_route = self.route_model.create(
            {
                "name": "Secondary Manufacture",
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Manufacture with secondary op",
                            "action": "manufacture",
                            "picking_type_id": self.op_type_2.id,
                            "location_src_id": self.source_loc_2.id,
                            "location_id": self.wh.lot_stock_id.id,
                        },
                    )
                ],
            }
        )
        self.product_2 = self.product_model.create(
            {"name": "Product 2", "route_ids": [(6, 0, self.secondary_manuf_route.ids)]}
        )

    def test_01_create_mo_and_change_product(self):
        new_mo = Form(self.env["mrp.production"])
        new_mo.product_id = self.product_1
        self.assertEqual(new_mo.picking_type_id, self.standard_manuf_op_type)
        new_mo.product_id = self.product_2
        self.assertEqual(new_mo.picking_type_id, self.op_type_2)
        new_mo.save()
        # Kept after save:
        self.assertEqual(new_mo.picking_type_id, self.op_type_2)

    def test_02_create_mo_change_op_type_manually(self):
        new_mo = Form(self.env["mrp.production"])
        new_mo.product_id = self.product_2
        self.assertEqual(new_mo.picking_type_id, self.op_type_2)
        new_mo.picking_type_id = self.standard_manuf_op_type
        self.assertEqual(new_mo.picking_type_id, self.standard_manuf_op_type)
        new_mo.save()
        # Kept after save:
        self.assertEqual(new_mo.picking_type_id, self.standard_manuf_op_type)
