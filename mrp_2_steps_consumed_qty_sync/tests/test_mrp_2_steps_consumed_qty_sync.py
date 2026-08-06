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

    def _add_product_stock(self, product, qty=50.0, location=None):
        return (
            self.env["stock.quant"]
            .with_context(inventory_mode=True)
            .create(
                {
                    "product_id": product.id,
                    "quantity": qty,
                    "location_id": (location or self.warehouse.lot_stock_id).id,
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

    def test_pick_backorder_keeps_pending_component_demand(self):
        with Form(self.warehouse) as warehouse:
            warehouse.reception_steps = "two_steps"
        # MO with two components: 50 uds of product_pending and 40 of
        # product_on_hand, which is the only one available in stock
        (production, _, _, product_pending, product_on_hand,) = self.generate_mo(
            qty_final=10,
            qty_base_1=5,
            qty_base_2=4,
            picking_type_id=self.warehouse.manu_type_id,
        )
        self._add_product_stock(product_on_hand)
        # product_pending is received but pending the second reception step,
        # so its goods are on input location and claimed by the MO
        self._add_product_stock(
            product_pending, location=self.warehouse.wh_input_stock_loc_id
        )
        self.assertEqual(product_pending.virtual_available, 0.0)
        # Prepare only the component on hand and validate creating a backorder
        pick_picking = production.picking_ids
        pick_picking.action_assign()
        for line in pick_picking.move_line_ids:
            line.qty_done = line.product_uom_qty
        pick_picking._action_done()
        # The backorder holds the pending component, the MO keeps its demand
        # and the incoming goods are not exposed to sales
        backorder = self.env["stock.picking"].search(
            [("backorder_id", "=", pick_picking.id)]
        )
        self.assertEqual(backorder.move_lines.product_id, product_pending)
        self.assertEqual(
            production.move_raw_ids.filtered(
                lambda sm: sm.product_id == product_pending
            ).product_uom_qty,
            50.0,
        )
        self.assertEqual(product_pending.virtual_available, 0.0)
