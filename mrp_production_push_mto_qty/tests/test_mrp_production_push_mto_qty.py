# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import Command
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMrpProductionPushMtoQty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.mto_route = cls.warehouse.mto_pull_id.route_id
        cls.mto_route.action_unarchive()
        cls.mto_route.rule_ids.procure_method = "make_to_order"
        cls.manufacture_route = cls.warehouse.manufacture_pull_id.route_id
        cls.warehouse.manu_type_id.push_mto_qty_to_dest_moves = True
        cls.component = cls.env["product.product"].create(
            {"name": "Component", "type": "consu"}
        )
        cls.product = cls._create_product("Finished", cls.component)

    @classmethod
    def _create_product(cls, name, component, component_qty=1.0):
        product = cls.env["product.product"].create(
            {
                "name": name,
                "is_storable": True,
                "route_ids": [
                    Command.link(cls.mto_route.id),
                    Command.link(cls.manufacture_route.id),
                ],
            }
        )
        cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_uom_id": product.uom_id.id,
                "product_qty": 1.0,
                "consumption": "flexible",
                "type": "normal",
                "bom_line_ids": [
                    Command.create(
                        {"product_id": component.id, "product_qty": component_qty}
                    )
                ],
            }
        )
        return product

    def _run_procurement(self, product, qty):
        self.env["stock.rule"].run(
            [
                self.env["stock.rule"].Procurement(
                    product,
                    qty,
                    self.uom_unit,
                    self.customer_location,
                    product.name,
                    "/",
                    self.env.company,
                    {"warehouse_id": self.warehouse},
                )
            ]
        )
        delivery_move = self.env["stock.move"].search(
            [
                ("product_id", "=", product.id),
                ("location_dest_id", "=", self.customer_location.id),
            ]
        )
        production = self.env["mrp.production"].search(
            [("product_id", "=", product.id)]
        )
        self.assertEqual(len(production), 1)
        return delivery_move, production

    def _produce(self, production, qty, backorder=False):
        """Produce `qty` and mark the production as done.

        Return the backorder production if any.
        """
        group_before = production.production_group_id.production_ids
        production.action_assign()
        with Form(production) as mo_form:
            mo_form.qty_producing = qty
        action = production.button_mark_done()
        if isinstance(action, dict) and action.get("res_model") == (
            "mrp.production.backorder"
        ):
            wizard = Form(
                self.env["mrp.production.backorder"].with_context(**action["context"])
            ).save()
            if backorder:
                wizard.action_backorder()
            else:
                wizard.action_close_mo()
        self.assertEqual(production.state, "done")
        return production.production_group_id.production_ids - group_before - production

    def test_produce_less_with_backorder(self):
        delivery_move, production = self._run_procurement(self.product, 10)
        backorder = self._produce(production, 8, backorder=True)
        self.assertEqual(backorder.product_qty, 2)
        self.assertEqual(delivery_move.product_uom_qty, 10)
        self.assertEqual(delivery_move.quantity, 8)

    def test_produce_less_without_backorder(self):
        delivery_move, production = self._run_procurement(self.product, 10)
        backorder = self._produce(production, 8)
        self.assertFalse(backorder)
        self.assertEqual(delivery_move.product_uom_qty, 8)
        self.assertEqual(delivery_move.quantity, 8)
        self.assertEqual(delivery_move.state, "assigned")

    def test_produce_more(self):
        delivery_move, production = self._run_procurement(self.product, 10)
        self._produce(production, 12)
        self.assertEqual(delivery_move.product_uom_qty, 12)
        self.assertEqual(delivery_move.quantity, 12)
        self.assertEqual(delivery_move.state, "assigned")

    def test_disabled(self):
        self.warehouse.manu_type_id.push_mto_qty_to_dest_moves = False
        delivery_move, production = self._run_procurement(self.product, 10)
        self._produce(production, 8)
        self.assertEqual(delivery_move.product_uom_qty, 10)

    def test_disabled_cancel_backorder(self):
        self.warehouse.manu_type_id.push_mto_qty_to_dest_moves = False
        delivery_move, production = self._run_procurement(self.product, 10)
        backorder = self._produce(production, 8, backorder=True)
        backorder.action_cancel()
        self.assertEqual(delivery_move.product_uom_qty, 10)

    def test_always_backorder(self):
        """button_mark_done calls itself when backorders are always created"""
        self.warehouse.manu_type_id.create_backorder = "always"
        delivery_move, production = self._run_procurement(self.product, 10)
        backorder = self._produce(production, 8)
        self.assertEqual(backorder.product_qty, 2)
        self.assertEqual(delivery_move.product_uom_qty, 10)
        self._produce(backorder, 3)
        self.assertEqual(delivery_move.product_uom_qty, 11)

    def test_backorder_produce_more(self):
        delivery_move, production = self._run_procurement(self.product, 10)
        backorder = self._produce(production, 8, backorder=True)
        self._produce(backorder, 3)
        self.assertEqual(delivery_move.product_uom_qty, 11)
        self.assertEqual(delivery_move.quantity, 11)

    def test_backorder_produce_less_without_backorder(self):
        delivery_move, production = self._run_procurement(self.product, 10)
        backorder = self._produce(production, 8, backorder=True)
        self._produce(backorder, 1)
        self.assertEqual(delivery_move.product_uom_qty, 9)
        self.assertEqual(delivery_move.quantity, 9)

    def test_backorder_produce_less_with_backorder(self):
        delivery_move, production = self._run_procurement(self.product, 10)
        backorder = self._produce(production, 8, backorder=True)
        backorder_2 = self._produce(backorder, 1, backorder=True)
        self.assertEqual(backorder_2.product_qty, 1)
        self.assertEqual(delivery_move.product_uom_qty, 10)
        self.assertEqual(delivery_move.quantity, 9)

    def test_cancel_backorder(self):
        delivery_move, production = self._run_procurement(self.product, 10)
        backorder = self._produce(production, 8, backorder=True)
        backorder.action_cancel()
        self.assertEqual(backorder.state, "cancel")
        self.assertEqual(delivery_move.product_uom_qty, 8)
        self.assertEqual(delivery_move.quantity, 8)
        self.assertEqual(delivery_move.state, "assigned")

    def test_cancel_backorder_cancels_empty_delivery_move(self):
        delivery_move, production = self._run_procurement(self.product, 10)
        backorder = self._produce(production, 8, backorder=True)
        picking = delivery_move.picking_id
        picking.move_ids.picked = True
        picking._action_done()
        self.assertEqual(delivery_move.state, "done")
        self.assertEqual(delivery_move.quantity, 8)
        delivery_backorder = picking.backorder_ids
        self.assertEqual(delivery_backorder.move_ids.product_uom_qty, 2)
        backorder.action_cancel()
        self.assertEqual(delivery_backorder.move_ids.state, "cancel")
        self.assertEqual(delivery_backorder.state, "cancel")

    def test_multi_step_delivery(self):
        self.warehouse.delivery_steps = "pick_ship"
        self._run_procurement(self.product, 10)
        production = self.env["mrp.production"].search(
            [("product_id", "=", self.product.id)]
        )
        pick_move = production.move_finished_ids.move_dest_ids
        self.assertEqual(pick_move.picking_type_id, self.warehouse.pick_type_id)
        self.assertEqual(pick_move.product_uom_qty, 10)
        self._produce(production, 12)
        self.assertEqual(pick_move.product_uom_qty, 12)
        self.assertEqual(pick_move.quantity, 12)
        # The ship move is pushed from the pick with the increased quantity
        pick_move.picked = True
        pick_move.picking_id._action_done()
        ship_move = pick_move.move_dest_ids
        self.assertEqual(ship_move.picking_type_id, self.warehouse.out_type_id)
        self.assertEqual(ship_move.product_uom_qty, 12)

    def test_chained_destination_moves(self):
        delivery_move, production = self._run_procurement(self.product, 10)
        next_move = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "product_uom_qty": 10,
                "product_uom": self.uom_unit.id,
                "location_id": self.customer_location.id,
                "location_dest_id": self.warehouse.lot_stock_id.id,
                "procure_method": "make_to_order",
                "move_orig_ids": [Command.link(delivery_move.id)],
            }
        )
        next_move._action_confirm(merge=False)
        self._produce(production, 7)
        self.assertEqual(delivery_move.product_uom_qty, 7)
        self.assertEqual(next_move.product_uom_qty, 7)

    def test_parent_production_components_untouched(self):
        parent_product = self.env["product.product"].create(
            {"name": "Parent", "is_storable": True}
        )
        self.env["mrp.bom"].create(
            {
                "product_tmpl_id": parent_product.product_tmpl_id.id,
                "product_uom_id": parent_product.uom_id.id,
                "product_qty": 1.0,
                "consumption": "flexible",
                "type": "normal",
                "bom_line_ids": [
                    Command.create({"product_id": self.product.id, "product_qty": 1})
                ],
            }
        )
        parent_production = self.env["mrp.production"].create(
            {"product_id": parent_product.id, "product_qty": 10}
        )
        parent_production.action_confirm()
        child_production = parent_production._get_children()
        self.assertEqual(child_production.product_id, self.product)
        raw_move = parent_production.move_raw_ids
        self.assertEqual(raw_move.product_uom_qty, 10)
        self._produce(child_production, 8)
        self.assertEqual(raw_move.product_uom_qty, 10)

    def _get_sam_moves(self, product):
        return self.env["stock.move"].search(
            [
                ("product_id", "=", product.id),
                ("picking_type_id", "=", self.warehouse.sam_type_id.id),
            ]
        )

    def test_three_steps_manufacturing_produce_less(self):
        """The post manufacturing move created by the push rule holds the
        produced quantity and must not be adjusted"""
        self.warehouse.manufacture_steps = "pbm_sam"
        delivery_move, production = self._run_procurement(self.product, 10)
        self.assertEqual(production.location_dest_id, self.warehouse.sam_loc_id)
        self._produce(production, 8)
        sam_move = self._get_sam_moves(self.product)
        self.assertEqual(len(sam_move), 1)
        self.assertEqual(sam_move.product_uom_qty, 8)
        self.assertEqual(sam_move.quantity, 8)
        self.assertEqual(sam_move.move_dest_ids, delivery_move)
        self.assertEqual(delivery_move.product_uom_qty, 8)
        # Store the products then deliver them all
        sam_move.picked = True
        sam_move.picking_id._action_done()
        self.assertEqual(delivery_move.quantity, 8)
        self.assertEqual(delivery_move.state, "assigned")

    def test_three_steps_manufacturing_produce_more(self):
        self.warehouse.manufacture_steps = "pbm_sam"
        delivery_move, production = self._run_procurement(self.product, 10)
        self._produce(production, 12)
        sam_move = self._get_sam_moves(self.product)
        self.assertEqual(sam_move.product_uom_qty, 12)
        self.assertEqual(sam_move.quantity, 12)
        self.assertEqual(delivery_move.product_uom_qty, 12)
        sam_move.picked = True
        sam_move.picking_id._action_done()
        self.assertEqual(delivery_move.quantity, 12)
        self.assertEqual(delivery_move.state, "assigned")

    def test_three_steps_manufacturing_backorder(self):
        self.warehouse.manufacture_steps = "pbm_sam"
        delivery_move, production = self._run_procurement(self.product, 10)
        backorder = self._produce(production, 8, backorder=True)
        sam_move = self._get_sam_moves(self.product)
        self.assertEqual(sam_move.product_uom_qty, 8)
        self.assertEqual(delivery_move.product_uom_qty, 10)
        self._produce(backorder, 3)
        # The store move of the backorder may be merged with the first one
        sam_moves = self._get_sam_moves(self.product)
        self.assertEqual(sum(sam_moves.mapped("product_uom_qty")), 11)
        self.assertEqual(sum(sam_moves.mapped("quantity")), 11)
        self.assertEqual(delivery_move.product_uom_qty, 11)
        sam_moves.picked = True
        sam_moves.picking_id._action_done()
        self.assertEqual(delivery_move.quantity, 11)
        self.assertEqual(delivery_move.state, "assigned")
