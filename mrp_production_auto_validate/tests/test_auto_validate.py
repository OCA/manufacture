# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, SavepointCase


class TestManufacturingOrderAutoValidate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Configure the WH to manufacture in at least two steps to get a
        # "pick components" transfer operation
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.wh.manufacture_steps = "pbm"
        # Configure the product to be replenished through manufacture route
        cls.product_template = cls.env.ref(
            "mrp.product_product_computer_desk_head_product_template"
        )
        cls.manufacture_route = cls.env.ref("mrp.route_warehouse0_manufacture")
        cls.product_template.route_ids = [(6, 0, [cls.manufacture_route.id])]
        # Configure the BoM to auto-validate manufacturing orders
        # NOTE: to ease tests we take a BoM with only one component
        cls.bom = cls.env.ref("mrp.mrp_bom_table_top")  # Tracked by S/N
        cls.bom.mo_auto_validation = True
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

    @classmethod
    def _replenish_product(cls, product, product_qty=1, product_uom=None):
        if product_uom is None:
            product_uom = cls.uom_unit
        wiz = (
            cls.env["product.replenish"]
            .with_context(default_product_id=product.id)
            .create(
                {
                    "quantity": product_qty,
                    "product_uom_id": product_uom.id,
                }
            )
        )
        wiz.launch_replenishment()

    @classmethod
    def _create_manufacturing_order(cls, bom, product_qty=1):
        with Form(cls.env["mrp.production"]) as form:
            form.bom_id = bom
            form.product_qty = product_qty
            order = form.save()
            order.invalidate_cache()
            return order

    @classmethod
    def _validate_picking(cls, picking, moves=None):
        """Validate a stock transfer.

        `moves` can be set with a list of tuples [(move, quantity_done)] to
        process the transfer partially.
        """
        if moves is None:
            moves = []
        for move in picking.move_lines:
            # Try to match a move to set a given qty
            for move2, qty_done in moves:
                if move == move2:
                    move.quantity_done = qty_done
                    break
            else:
                move.quantity_done = move.product_uom_qty
        picking._action_done()

    def test_bom_alert(self):
        self.assertIn(
            "restricted to the BoM Quantity", self.bom.mo_auto_validation_warning
        )

    def test_get_manufacturing_orders_pbm(self):
        """Get the MO from transfers in a 2 steps configuration."""
        # WH already configured as 'Pick components and then manufacture (2 steps)'
        order = self._create_manufacturing_order(self.bom)
        order.action_confirm()
        picking_pick = order.picking_ids
        self.assertEqual(picking_pick._get_manufacturing_orders(), order)

    def test_get_manufacturing_orders_pbm_sam(self):
        """Get the MO from transfers in a 3 steps configuration."""
        self.wh.manufacture_steps = "pbm_sam"
        order = self._create_manufacturing_order(self.bom)
        order.action_confirm()
        picking_pick = order.picking_ids.filtered(
            lambda o: "Pick" in o.picking_type_id.name
        )
        picking_store = order.picking_ids.filtered(
            lambda o: "Store" in o.picking_type_id.name
        )
        self.assertEqual(picking_pick._get_manufacturing_orders(), order)
        self.assertFalse(picking_store._get_manufacturing_orders())

    def test_create_order_too_much_qty_to_produce(self):
        """Creation of MO for 2 finished product while BoM produces 1."""
        with self.assertRaisesRegex(ValidationError, r"is restricted to"):
            self._create_manufacturing_order(self.bom, product_qty=2)

    def test_auto_validate_disabled(self):
        """Auto-validation of MO disabled. No change in the standard behavior."""
        self.bom.mo_auto_validation = False
        order = self._create_manufacturing_order(self.bom)
        order.action_confirm()
        self.assertEqual(order.state, "confirmed")
        picking = order.picking_ids
        picking.action_assign()
        self.assertEqual(picking.state, "assigned")
        self._validate_picking(picking)
        self.assertEqual(picking.state, "done")
        self.assertEqual(order.state, "confirmed")

    def test_auto_validate_one_qty_to_produce(self):
        """Auto-validation of MO with components for 1 finished product."""
        order = self._create_manufacturing_order(self.bom)
        order.action_confirm()
        self.assertEqual(order.state, "confirmed")
        picking = order.picking_ids
        picking.action_assign()
        self.assertEqual(picking.state, "assigned")
        self._validate_picking(picking)
        self.assertEqual(picking.state, "done")
        self.assertEqual(order.state, "done")
        self.assertTrue(order.lot_producing_id)

    def test_auto_validate_two_qty_to_produce(self):
        """Auto-validation of MO with components for 2 finished product."""
        self.bom.product_qty = 2
        order = self._create_manufacturing_order(self.bom, product_qty=2)
        order.action_confirm()
        self.assertEqual(order.state, "confirmed")
        picking = order.picking_ids
        picking.action_assign()
        self.assertEqual(picking.state, "assigned")
        self._validate_picking(picking)
        self.assertEqual(picking.state, "done")
        self.assertEqual(order.state, "done")
        self.assertTrue(order.lot_producing_id)

    def test_auto_validate_with_not_enough_components(self):
        """MO not validated: not enough components to produce 1 finished product."""
        self.bom.product_qty = 2
        self.bom.bom_line_ids.product_qty = 4
        order = self._create_manufacturing_order(self.bom, product_qty=2)
        order.action_confirm()
        self.assertEqual(order.state, "confirmed")
        # Process 'Pick components' with not enough qties to process at least
        # 1 finished product (2 components required but only 1 transfered)
        picking = order.picking_ids
        picking.action_assign()
        self.assertEqual(picking.state, "assigned")
        self._validate_picking(picking, moves=[(picking.move_lines, 1)])
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.backorder_ids.move_lines.product_uom_qty, 3)
        # Check that no MO gets validated in the process
        order_done = picking._get_manufacturing_orders(states=("done",))
        self.assertFalse(order_done)
        self.assertEqual(order.state, "confirmed")
        self.assertEqual(order.product_qty, 2)

    def test_keep_qty_on_replenishment(self):
        existing_mos = self.env["mrp.production"].search([])
        self._replenish_product(self.product_template.product_variant_id, product_qty=1)
        created_mos = self.env["mrp.production"].search(
            [("id", "not in", existing_mos.ids)]
        )
        self.assertEqual(len(created_mos), 1)
        self.assertEqual(created_mos.product_qty, self.bom.product_qty)
        self.assertFalse(any("split" in m.body for m in created_mos.message_ids))
        self.assertFalse(any("increased" in m.body for m in created_mos.message_ids))

    def test_split_qty_on_replenishment(self):
        existing_mos = self.env["mrp.production"].search([])
        self._replenish_product(self.product_template.product_variant_id, product_qty=3)
        created_mos = self.env["mrp.production"].search(
            [("id", "not in", existing_mos.ids)]
        )
        self.assertEqual(len(created_mos), 3)
        for mo in created_mos:
            self.assertEqual(mo.product_qty, self.bom.product_qty)
            self.assertTrue(any("split" in m.body for m in mo.message_ids))

    def test_raise_qty_on_replenishment(self):
        existing_mos = self.env["mrp.production"].search([])
        self.bom.product_qty = 5
        self._replenish_product(self.product_template.product_variant_id, product_qty=3)
        created_mos = self.env["mrp.production"].search(
            [("id", "not in", existing_mos.ids)]
        )
        self.assertEqual(len(created_mos), 1)
        self.assertEqual(created_mos.product_qty, self.bom.product_qty)
        self.assertTrue(any("increased" in m.body for m in created_mos.message_ids))
