# Copyright 2024 Tecnativa - Sergio Teruel
# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import Form, tagged

from odoo.addons.mrp.tests.common import TestMrpCommon


@tagged("post_install", "-at_install")
class TestMrp2StepsConsumedQtySync(TestMrpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(cls.env.context, test_mrp_2_steps_consumed_qty_sync=True)
        )
        # Active multilocation security group and multi step routes
        grp_multi_loc = cls.env.ref("stock.group_stock_multi_locations")
        grp_multi_routes = cls.env.ref("stock.group_adv_location")
        cls.env.user.write({"groups_id": [(4, grp_multi_loc.id)]})
        cls.env.user.write({"groups_id": [(4, grp_multi_routes.id)]})
        # Work orders are only shown in the production form with this group
        grp_routings = cls.env.ref("mrp.group_mrp_routings")
        cls.env.user.write({"groups_id": [(4, grp_routings.id)]})

        # Active produce in two steps
        cls.warehouse = cls.env.ref("stock.warehouse0")
        with Form(cls.warehouse) as warehouse:
            warehouse.manufacture_steps = "pbm"
        # Some instances require choosing where the finished product goes
        cls.finished_location = cls.env["stock.location"].create(
            {"name": "Finished products", "location_id": cls.warehouse.lot_stock_id.id}
        )

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
        ).quantity = 10
        pick_picking.move_line_ids.filtered(
            lambda sml: sml.product_id == product_to_use_2
        ).quantity = 15
        pick_picking.move_ids.picked = True
        pick_picking._action_done()

        # Check if the done quantities are sync to raw material in mo order
        self.assertEqual(
            production.move_raw_ids.filtered(
                lambda sm: sm.product_id == product_to_use_1
            ).quantity,
            10.0,
        )
        self.assertEqual(
            production.move_raw_ids.filtered(
                lambda sm: sm.product_id == product_to_use_2
            ).quantity,
            15.0,
        )

    def test_pick_backorder_keeps_pending_component_demand(self):
        with Form(self.warehouse) as warehouse:
            warehouse.reception_steps = "two_steps"
        # MO with two components: 50 uds of product_pending and 40 of
        # product_on_hand, which is the only one available in stock
        (
            production,
            _,
            _,
            product_pending,
            product_on_hand,
        ) = self.generate_mo(
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
        action = pick_picking.button_validate()
        Form(
            self.env["stock.backorder.confirmation"].with_context(**action["context"])
        ).save().process()
        # The backorder holds the pending component, the MO keeps its demand
        # and the incoming goods are not exposed to sales
        backorder = self.env["stock.picking"].search(
            [("backorder_id", "=", pick_picking.id)]
        )
        self.assertEqual(backorder.move_ids.product_id, product_pending)
        self.assertEqual(
            production.move_raw_ids.filtered(
                lambda sm: sm.product_id == product_pending
            ).product_uom_qty,
            50.0,
        )
        self.assertEqual(product_pending.virtual_available, 0.0)

    def _create_production_with_operation(self):
        """MO of 10 units with one operation and two components: 50 units of
        product_picked, which has stock, and 40 of product_pending, which has
        none.
        """
        product_to_build, product_picked, product_pending = self.env[
            "product.product"
        ].create(
            [
                {"name": "Test finished", "is_storable": True},
                {"name": "Test component picked", "is_storable": True},
                {"name": "Test component pending", "is_storable": True},
            ]
        )
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": product_to_build.product_tmpl_id.id,
                "product_qty": 1.0,
                "consumption": "flexible",
                "bom_line_ids": [
                    (0, 0, {"product_id": product_picked.id, "product_qty": 5}),
                    (0, 0, {"product_id": product_pending.id, "product_qty": 4}),
                ],
                "operation_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test operation",
                            "workcenter_id": self.workcenter_1.id,
                            "time_cycle": 10,
                        },
                    )
                ],
            }
        )
        self._add_product_stock(product_picked)
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = product_to_build
        mo_form.picking_type_id = self.warehouse.manu_type_id
        mo_form.bom_id = bom
        mo_form.product_qty = 10
        mo_form.location_dest_id = self.finished_location
        production = mo_form.save()
        production.action_confirm()
        return production, product_picked, product_pending

    def _pick_available_components(self, production, product_pending):
        """Pick only the component with stock and validate creating a backorder,
        so product_pending stays in the pick components backorder.
        """
        pick_picking = production.picking_ids
        pick_picking.action_assign()
        action = pick_picking.button_validate()
        Form(
            self.env["stock.backorder.confirmation"].with_context(**action["context"])
        ).save().process()
        self.assertEqual(
            pick_picking.backorder_ids.move_ids.product_id, product_pending
        )

    def _consumed(self, production, product):
        """Quantity to consume, or consumed when the production is done"""
        return sum(
            production.move_raw_ids.filtered(
                lambda sm: sm.product_id == product and sm.state != "cancel"
            ).mapped("quantity")
        )

    def _assert_consumed(self, production, products_qty):
        for product, qty in products_qty.items():
            self.assertEqual(self._consumed(production, product), qty)

    def test_start_workorder_keeps_pending_component_unconsumed(self):
        production, product_picked, product_pending = (
            self._create_production_with_operation()
        )
        self._pick_available_components(production, product_pending)
        production.workorder_ids.button_start()
        self.assertEqual(production.qty_producing, 10.0)
        self._assert_consumed(production, {product_picked: 50.0, product_pending: 0.0})

    def test_set_qty_producing_keeps_pending_component_unconsumed(self):
        production, product_picked, product_pending = (
            self._create_production_with_operation()
        )
        self._pick_available_components(production, product_pending)
        with Form(production) as mo_form:
            mo_form.qty_producing = 10
        self._assert_consumed(production, {product_picked: 50.0, product_pending: 0.0})

    def test_finish_workorder_keeps_pending_component_unconsumed(self):
        production, product_picked, product_pending = (
            self._create_production_with_operation()
        )
        self._pick_available_components(production, product_pending)
        production.workorder_ids.button_start()
        production.workorder_ids.button_finish()
        self._assert_consumed(production, {product_picked: 50.0, product_pending: 0.0})

    def test_set_qty_producing_before_pick_consumes_nothing(self):
        production, product_picked, product_pending = (
            self._create_production_with_operation()
        )
        with Form(production) as mo_form:
            mo_form.qty_producing = 10
        self._assert_consumed(production, {product_picked: 0.0, product_pending: 0.0})

    def test_set_qty_producing_one_step_consumes_as_core(self):
        """Components that do not come from a pick components picking keep the
        core behavior and are consumed in proportion to the BoM.
        """
        with Form(self.warehouse) as warehouse:
            warehouse.manufacture_steps = "mrp_one_step"
        production, product_picked, product_pending = (
            self._create_production_with_operation()
        )
        with Form(production) as mo_form:
            mo_form.qty_producing = 10
        self._assert_consumed(production, {product_picked: 50.0, product_pending: 40.0})

    def test_start_workorder_before_pick_keeps_only_picked_consumption(self):
        production, product_picked, product_pending = (
            self._create_production_with_operation()
        )
        production.workorder_ids.button_start()
        self.assertEqual(production.qty_producing, 10.0)
        self._assert_consumed(production, {product_picked: 0.0, product_pending: 0.0})
        self._pick_available_components(production, product_pending)
        self._assert_consumed(production, {product_picked: 50.0, product_pending: 0.0})

    def test_set_qty_producing_keeps_picked_consumption(self):
        """Consumption of a fully picked component is the picked quantity, so
        producing less than planned does not scale it down.
        """
        production, product_picked, product_pending = (
            self._create_production_with_operation()
        )
        self._pick_available_components(production, product_pending)
        with Form(production) as mo_form:
            mo_form.qty_producing = 8
        self._assert_consumed(production, {product_picked: 50.0, product_pending: 0.0})

    def _mark_done_producing_8(self, production):
        with Form(production) as mo_form:
            mo_form.qty_producing = 8
        action = production.button_mark_done()
        return Form(
            self.env["mrp.production.backorder"].with_context(**action["context"])
        ).save()

    def test_production_backorder_splits_picked_consumption(self):
        production, product_picked, product_pending = (
            self._create_production_with_operation()
        )
        self._pick_available_components(production, product_pending)
        self._mark_done_producing_8(production).action_backorder()
        backorder = production.procurement_group_id.mrp_production_ids - production
        # The production consumes the part of the picked quantities proportional
        # to the quantity produced, and nothing of the component pending to pick
        self._assert_consumed(production, {product_picked: 40.0, product_pending: 0.0})
        # The backorder consumes the rest of the picked quantities
        bo_picked_move = backorder.move_raw_ids.filtered(
            lambda sm: sm.product_id == product_picked
        )
        self.assertEqual(bo_picked_move.product_uom_qty, 10.0)
        self._assert_consumed(backorder, {product_picked: 10.0, product_pending: 0.0})
        # Picking the pending component later keeps the demand of the other one
        self._add_product_stock(product_pending)
        pick_backorder = backorder.picking_ids.filtered(
            lambda p: p.state not in ("done", "cancel")
        )
        pick_backorder.action_assign()
        pick_backorder.move_ids.quantity = 8
        action = pick_backorder.button_validate()
        Form(
            self.env["stock.backorder.confirmation"].with_context(**action["context"])
        ).save().process_cancel_backorder()
        self.assertEqual(bo_picked_move.product_uom_qty, 10.0)
        self._assert_consumed(backorder, {product_picked: 10.0, product_pending: 8.0})

    def test_close_production_without_backorder_consumes_all_picked(self):
        production, product_picked, product_pending = (
            self._create_production_with_operation()
        )
        self._pick_available_components(production, product_pending)
        self._mark_done_producing_8(production).action_close_mo()
        self.assertEqual(production.state, "done")
        self._assert_consumed(production, {product_picked: 50.0, product_pending: 0.0})
