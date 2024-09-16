# Copyright 2024 Tecnativa - Sergio Teruel
# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import tagged
from odoo.tests.common import Form

from odoo.addons.mrp.tests.common import TestMrpCommon


@tagged("post_install", "-at_install")
class TestMrp2StepsConsumedQtySync(TestMrpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Active multilocation security group and multi step routes
        grp_multi_loc = cls.env.ref("stock.group_stock_multi_locations")
        grp_multi_routes = cls.env.ref("stock.group_adv_location")
        cls.env.user.write({"groups_id": [(4, grp_multi_loc.id)]})
        cls.env.user.write({"groups_id": [(4, grp_multi_routes.id)]})

        # Active produce in two steps
        cls.warehouse = cls.env.ref("stock.warehouse0")
        with Form(cls.warehouse) as warehouse:
            warehouse.manufacture_steps = "pbm"

    def _add_product_stock(self, product, qty=50.0):
        return (
            self.env["stock.quant"]
            .with_context(inventory_mode=True)
            .create(
                {
                    "product_id": product.id,
                    "quantity": qty,
                    "location_id": self.warehouse.lot_stock_id.id,
                }
            )
        )

    def test_consumed_qty_production_order(self):
        # Generate manufacturer order
        (
            production,
            _,
            product_to_build,
            product_to_use_1,
            product_to_use_2,
        ) = self.generate_mo(
            qty_final=10,
            qty_base_1=5,
            qty_base_2=4,
            picking_type_id=self.warehouse.manu_type_id,
        )

        # Set stock for components
        self._add_product_stock(product_to_use_1)
        self._add_product_stock(product_to_use_2)

        # Complete pick components
        pick_picking = production.picking_ids
        pick_picking.action_assign()
        pick_picking.move_line_ids.filtered(
            lambda sml: sml.product_id == product_to_use_1
        ).qty_done = 10
        pick_picking.move_line_ids.filtered(
            lambda sml: sml.product_id == product_to_use_2
        ).qty_done = 15
        pick_picking._action_done()

        # Check if the done quantities are sync to raw material in mo order
        self.assertEqual(
            production.move_raw_ids.filtered(
                lambda sm: sm.product_id == product_to_use_1
            ).quantity_done,
            10.0,
        )
        self.assertEqual(
            production.move_raw_ids.filtered(
                lambda sm: sm.product_id == product_to_use_2
            ).quantity_done,
            15.0,
        )
