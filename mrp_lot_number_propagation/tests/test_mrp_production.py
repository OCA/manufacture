# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests import Form

from .common import Common


class TestMrpProduction(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._configure_bom()
        cls._configure_single_component_bom()
        cls.order = cls._create_order(cls.bom_product_product, cls.bom)
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

    @classmethod
    def _configure_single_component_bom(cls):
        cls.finished_propagated_product = cls.env["product.product"].create(
            {"name": "Finished serial", "is_storable": True, "tracking": "serial"}
        )
        cls.component_propagated_product = cls.env["product.product"].create(
            {"name": "Component serial", "is_storable": True, "tracking": "serial"}
        )
        cls.propagate_bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.finished_propagated_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "lot_number_propagation": True,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.component_propagated_product.id,
                            "product_qty": 1,
                            "propagate_lot_number": True,
                        },
                    )
                ],
            }
        )

    @classmethod
    def _configure_bom(cls):
        bom_form = Form(cls.bom)
        bom_form.lot_number_propagation = True
        with bom_form.bom_line_ids.edit(0) as line_form:  # Line tracked by SN
            line_form.propagate_lot_number = True
        return bom_form.save()

    @classmethod
    def _create_order(cls, product, bom, qty=1):
        form = Form(cls.env["mrp.production"])
        form.product_id = product
        form.bom_id = bom
        form.product_qty = qty
        return form.save()

    def _set_qty_done(self, order):
        for line in order.move_raw_ids.move_line_ids:
            line.quantity = line.quantity_product_uom
            line.picked = True
        order.qty_producing = order.product_qty

    def test_order_propagated_lot_producing(self):
        self.assertTrue(self.order.is_lot_number_propagated)  # set by onchange
        self._update_stock_component_qty(self.order)
        self.order.action_confirm()
        self.assertTrue(self.order.is_lot_number_propagated)  # set by action_confirm
        self.assertTrue(any(self.order.move_raw_ids.mapped("propagate_lot_number")))
        self._set_qty_done(self.order)
        self.assertEqual(self.order.propagated_lot_producing, self.LOT_NAME)

    def test_order_write_lot_producing_ids_not_allowed(self):
        with self.assertRaisesRegex(UserError, "not allowed"):
            self.order.write({"lot_producing_ids": "test"})

    def test_order_post_inventory(self):
        self._update_stock_component_qty(self.order)
        self.order.action_confirm()
        self._set_qty_done(self.order)
        self.order.button_mark_done()
        self.assertEqual(self.order.lot_producing_ids.name, self.LOT_NAME)

    def test_order_post_inventory_lot_already_exists_but_not_used(self):
        self._update_stock_component_qty(self.order)
        self.order.action_confirm()
        self._set_qty_done(self.order)
        self.assertEqual(self.order.propagated_lot_producing, self.LOT_NAME)
        # Create a lot with the same number for the finished product
        # without any stock/quants (so not used at all) before validating the MO
        existing_lot = self.env["stock.lot"].create(
            {
                "product_id": self.order.product_id.id,
                "company_id": self.order.company_id.id,
                "name": self.order.propagated_lot_producing,
            }
        )
        self.order.button_mark_done()
        self.assertEqual(self.order.lot_producing_ids, existing_lot)

    def test_order_post_inventory_lot_already_exists_and_used(self):
        self._update_stock_component_qty(self.order)
        self.order.action_confirm()
        self._set_qty_done(self.order)
        self.assertEqual(self.order.propagated_lot_producing, self.LOT_NAME)
        # Create a lot with the same number for the finished product
        # with some stock/quants (so it is considered as used) before
        # validating the MO
        existing_lot = self.env["stock.lot"].create(
            {
                "product_id": self.order.product_id.id,
                "company_id": self.order.company_id.id,
                "name": self.order.propagated_lot_producing,
            }
        )
        self._update_qty_in_location(
            self.env.ref("stock.stock_location_stock"),
            self.order.product_id,
            1,
            lot=existing_lot,
        )
        with self.assertRaisesRegex(UserError, "already exists and has been used"):
            self.order.button_mark_done()

    def _assign_finished_lot(self, order, lot):
        """Assign a finished lot to the order, bypassing the write guard."""
        order.with_context(lot_propagation=True).lot_producing_ids = lot

    def _prepare_unreserved_component_move(
        self, used_finished_lot=False, remove_component_stock=True
    ):
        """Confirm an order with a finished lot assigned, then unreserve.

        Returns ``(move, lot)``; the caller re-reserves the component move
        with ``move._action_assign()`` and asserts the outcome.
        """
        self._update_stock_component_qty(self.order)
        self.order.action_confirm()
        lot = self.env["stock.lot"].create(
            {
                "product_id": self.order.product_id.id,
                "company_id": self.order.company_id.id,
                "name": self.LOT_NAME,
            }
        )
        if used_finished_lot:
            self._update_qty_in_location(
                self.stock_location, self.order.product_id, 1, lot=lot
            )
        self._assign_finished_lot(self.order, lot)
        move = self.order._get_propagating_component_move()
        move._do_unreserve()
        if remove_component_stock:
            # remove the serial from stock: re-reservation cannot find it,
            #  so the assigned finished lot no longer matches any component
            #  serial
            self.env["stock.quant"]._update_available_quantity(
                self.product_tracked_by_sn,
                self.stock_location,
                -1,
                lot_id=self.existing_lot,
            )
        return move, lot

    def test_assign_component_move_keeps_matching_finished_lot(self):
        """Re-reserving the same component serials keeps the finished lots."""
        move, lot = self._prepare_unreserved_component_move(
            remove_component_stock=False
        )
        # re-reservation finds the same serial: nothing to clean up
        move._action_assign()
        self.assertEqual(self.order.lot_producing_ids, lot)

    def test_unreserve_component_move_clears_outdated_finished_lot(self):
        """Component serial no longer reserved: the finished lot is stale.

        The unused finished lot must be removed from the order and deleted.
        """
        move, lot = self._prepare_unreserved_component_move()
        move._action_assign()
        self.assertFalse(self.order.lot_producing_ids)
        # the finished lot was unused, it must have been deleted
        self.assertFalse(lot.exists())

    def test_unreserve_component_move_keeps_used_finished_lot(self):
        """Same as above, but the finished lot already has stock: keep it."""
        move, lot = self._prepare_unreserved_component_move(used_finished_lot=True)
        move._action_assign()
        # the finished lot is detached from the order...
        self.assertFalse(self.order.lot_producing_ids)
        # ...but it is kept, as it holds stock
        self.assertTrue(lot.exists())

    def test_confirm_with_variant_ok(self):
        self._add_trucks_variants(self.bom_product_template)
        self._add_trucks_variants(self.product_template_tracked_by_sn)
        new_bom = self._create_bom_with_variants()
        self.assertTrue(new_bom.lot_number_propagation)
        # As all variants must have a single component
        #  where lot must be propagated, there should not be any error
        for product in self.bom_product_template.product_variant_ids:
            new_order = self._create_order(product, new_bom)
            new_order.action_confirm()

    def test_confirm_with_variant_multiple(self):
        self._add_trucks_variants(self.bom_product_template)
        self._add_trucks_variants(self.product_template_tracked_by_sn)
        new_bom = self._create_bom_with_variants()
        # Remove application on variant for first bom line
        #  with this only the first variant of the product template
        #  will have a single component where lot must be propagated
        new_bom.bom_line_ids[0].bom_product_template_attribute_value_ids = [
            Command.clear()
        ]
        for cnt, product in enumerate(self.bom_product_template.product_variant_ids):
            new_order = self._create_order(product, new_bom)
            if cnt == 0:
                new_order.action_confirm()
            else:
                with self.assertRaisesRegex(UserError, "multiple components"):
                    new_order.action_confirm()

    def test_confirm_with_variant_no(self):
        self._add_trucks_variants(self.bom_product_template)
        self._add_trucks_variants(self.product_template_tracked_by_sn)
        new_bom = self._create_bom_with_variants()
        # Remove first bom line
        #  with this the first variant of the product template
        #  will not have any component where lot must be propagated
        new_bom.bom_line_ids[0].unlink()
        for cnt, product in enumerate(self.bom_product_template.product_variant_ids):
            new_order = self._create_order(product, new_bom)
            if cnt == 0:
                with self.assertRaisesRegex(UserError, "no component"):
                    new_order.action_confirm()
            else:
                new_order.action_confirm()

    def test_production_serials_wizard(self):
        order = self._create_order(self.bom_product_product, self.bom, qty=5)
        self._update_stock_component_qty(order)
        order.action_confirm()
        tracked_moves = order.move_raw_ids.filtered(
            lambda mv: mv.product_id.tracking != "none"
        )
        self.assertTrue(len(tracked_moves) > 1)
        res = order.button_mark_done()
        self.assertEqual(type(res), dict)
        self.assertEqual(res["res_model"], "mrp.production.serials")

        propagate_move = order._get_propagating_component_move()
        component_names = propagate_move.move_line_ids.lot_id.mapped("name")

        wizard = Form(
            self.env["mrp.production.serials"].with_context(**res["context"])
        ).save()

        # The serial numbers are readonly in the view (force_save keeps the
        #  prefilled value on save) and pre-filled with the serials reserved
        #  on the propagating component
        self.assertTrue(wizard.is_lot_number_propagated)
        self.assertEqual(
            sorted(wizard.serial_numbers.split("\n")), sorted(component_names)
        )

        # Simulate a tampered value (readonly is a view-level modifier only):
        #  serials not matching the propagating component must raise an error
        wizard.serial_numbers = "\n".join([f"random-serial-{i}" for i in range(5)])
        with self.assertRaisesRegex(
            UserError, "set to propagate lot number from component"
        ):
            wizard.action_apply()

        # Restore the serials of the propagating component (one per line)
        wizard.serial_numbers = "\n".join(component_names)
        wizard.action_apply()

        # The wizard only assigns the serials, the MO is not marked as done yet
        self.assertNotEqual(order.state, "done")
        self.assertEqual(
            sorted(order.lot_producing_ids.mapped("name")), sorted(component_names)
        )

        # Mark done again, now that serials are assigned
        order.button_mark_done()
        self.assertEqual(order.state, "done")
