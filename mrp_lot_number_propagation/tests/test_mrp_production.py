# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime

from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests.common import Form

from .common import Common


class TestMrpProduction(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Configure the BoM to propagate lot number
        cls._configure_bom()
        cls.order = cls._create_order(cls.bom_product_product, cls.bom)

    @classmethod
    def _configure_bom(cls):
        with Form(cls.bom) as form:
            form.lot_number_propagation = True
            line_form = form.bom_line_ids.edit(0)  # Line tracked by SN
            line_form.propagate_lot_number = True
            line_form.save()
            form.save()

    @classmethod
    def _create_order(cls, product, bom):
        with Form(cls.env["mrp.production"]) as form:
            form.product_id = product
            form.bom_id = bom
            return form.save()

    def _set_qty_done(self, order):
        for line in order.move_raw_ids.move_line_ids:
            line.qty_done = line.reserved_uom_qty
        order.qty_producing = order.product_qty

    def test_order_propagated_lot_producing(self):
        self.assertTrue(self.order.is_lot_number_propagated)  # set by onchange
        self._update_stock_component_qty(self.order)
        self.order.action_confirm()
        self.assertTrue(self.order.is_lot_number_propagated)  # set by action_confirm
        self.assertTrue(any(self.order.move_raw_ids.mapped("propagate_lot_number")))
        self._set_qty_done(self.order)
        self.assertEqual(self.order.propagated_lot_producing, self.LOT_NAME)

    def test_order_post_inventory(self):
        self._update_stock_component_qty(self.order)
        self.order.action_confirm()
        self._set_qty_done(self.order)
        self.order.button_mark_done()
        self.assertEqual(self.order.lot_producing_id.name, self.LOT_NAME)

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
        self.assertEqual(self.order.lot_producing_id, existing_lot)

    # def test_order_post_inventory_lot_already_exists_and_used(self):
    #     self._update_stock_component_qty(self.order)
    #     self.order.action_confirm()
    #     self._set_qty_done(self.order)
    #     self.assertEqual(self.order.propagated_lot_producing, self.LOT_NAME)
    #     # Create a lot with the same number for the finished product
    #     # with some stock/quants (so it is considered as used) before
    #     # validating the MO
    #     existing_lot = self.env["stock.lot"].create(
    #         {
    #             "product_id": self.order.product_id.id,
    #             "company_id": self.order.company_id.id,
    #             "name": self.order.propagated_lot_producing,
    #         }
    #     )
    #     self._update_qty_in_location(
    #         self.env.ref("stock.stock_location_stock"),
    #         self.order.product_id,
    #         1,
    #         lot=existing_lot,
    #     )
    #     with self.assertRaisesRegex(UserError, "already exists and has been used"):
    #         self.order.button_mark_done()
    #     with self.assertRaisesRegex(UserError, "already exists and has been used"):
    #         self.order._create_and_assign_propagated_lot_number()

    def test_confirm_with_variant_ok(self):
        self._add_color_and_legs_variants(self.bom_product_template)
        self._add_color_and_legs_variants(self.product_template_tracked_by_sn)
        new_bom = self._create_bom_with_variants()
        self.assertTrue(new_bom.lot_number_propagation)
        # As all variants must have a single component
        #  where lot must be propagated, there should not be any error
        for product in self.bom_product_template.product_variant_ids:
            new_order = self._create_order(product, new_bom)
            new_order.action_confirm()

    def test_confirm_with_variant_multiple(self):
        self._add_color_and_legs_variants(self.bom_product_template)
        self._add_color_and_legs_variants(self.product_template_tracked_by_sn)
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
        self._add_color_and_legs_variants(self.bom_product_template)
        self._add_color_and_legs_variants(self.product_template_tracked_by_sn)
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

    def test_lot_propagation_full_flow(self):
        """Test complete lot propagation flow with multiple components"""

        component_with_lot = self.product_tracked_by_lot  # tracked by lot
        component_no_tracking = self.line_no_tracking.product_id

        final_product = self.env["product.product"].create(
            {
                "name": "Test Final Lot Product",
                "type": "product",
                "tracking": "lot",
                "categ_id": component_with_lot.categ_id.id,
                "uom_id": component_with_lot.uom_id.id,
                "uom_po_id": component_with_lot.uom_po_id.id,
            }
        )

        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": final_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    # Componente CON lote (PROPAGAR)
                    (
                        0,
                        0,
                        {
                            "product_id": component_with_lot.id,
                            "product_qty": 1.0,
                            "propagate_lot_number": True,
                        },
                    ),
                    # Componente SIN tracking (etiqueta, envoltorio, etc.)
                    (
                        0,
                        0,
                        {
                            "product_id": component_no_tracking.id,
                            "product_qty": 1.0,
                            "propagate_lot_number": False,
                        },
                    ),
                ],
                "lot_number_propagation": True,
            }
        )

        self.assertTrue(bom.display_lot_number_propagation)
        self.assertTrue(bom.lot_number_propagation)

        propagating_lines = bom.bom_line_ids.filtered("propagate_lot_number")
        self.assertEqual(len(propagating_lines), 1)
        self.assertEqual(propagating_lines.product_id, component_with_lot)

        mo = self.env["mrp.production"].create(
            {
                "product_id": final_product.id,
                "product_qty": 1.0,
                "bom_id": bom.id,
            }
        )

        self._update_stock_component_qty(mo, bom)
        mo.action_confirm()
        self.assertTrue(mo.is_lot_number_propagated)
        self.assertTrue(mo.propagated_lot_producing)
        self.assertEqual(mo.propagated_lot_producing, self.LOT_NAME)
        self.assertFalse(mo.lot_producing_id)

        lot_to_propagate = self.env["stock.lot"].search(
            [
                ("name", "=", mo.propagated_lot_producing),
                ("company_id", "=", mo.company_id.id),
            ],
            limit=1,
        )

        expiration_date = datetime(2027, 12, 31)
        if lot_to_propagate:
            lot_to_propagate.expiration_date = expiration_date
        mo._get_propagating_component_move()

        self.assertEqual(len(mo.move_raw_ids), 2)
        propagating_moves = mo.move_raw_ids.filtered("propagate_lot_number")
        self.assertEqual(len(propagating_moves), 1)

        mo.action_assign()
        self._set_qty_done(mo)
        self.assertEqual(mo.propagated_lot_producing, self.LOT_NAME)

        mo.button_mark_done()
        self.assertEqual(mo.lot_producing_id.name, self.LOT_NAME)
        self.assertEqual(mo.lot_producing_id.expiration_date, expiration_date)

        for move in mo.move_raw_ids:
            self.assertEqual(move.state, "done")
            self.assertEqual(move.quantity_done, move.product_uom_qty)

    def test_lot_propagation_multiple_propagation_error(self):
        """Test lot propagation flow erro due to multiple components propagating"""

        component_with_lot = self.product_tracked_by_lot
        component_no_tracking = self.line_no_tracking.product_id
        component_no_tracking.tracking = "lot"

        final_product = self.env["product.product"].create(
            {
                "name": "Test Final Lot Product Multiple Error",
                "type": "product",
                "tracking": "lot",
                "categ_id": component_with_lot.categ_id.id,
                "uom_id": component_with_lot.uom_id.id,
                "uom_po_id": component_with_lot.uom_po_id.id,
            }
        )

        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": final_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": component_with_lot.id,
                            "product_qty": 1.0,
                            "propagate_lot_number": True,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": component_no_tracking.id,
                            "product_qty": 1.0,
                            "propagate_lot_number": True,
                        },
                    ),
                ],
                "lot_number_propagation": True,
            }
        )

        self.assertTrue(bom.display_lot_number_propagation)
        self.assertTrue(bom.lot_number_propagation)

        propagating_lines = bom.bom_line_ids.filtered("propagate_lot_number")
        self.assertEqual(len(propagating_lines), 2)

        mo = self.env["mrp.production"].create(
            {
                "product_id": final_product.id,
                "product_qty": 1.0,
                "bom_id": bom.id,
            }
        )

        self._update_stock_component_qty(mo, bom)

        with self.assertRaisesRegex(
            UserError, "multiple components propagating lot number"
        ):
            mo.action_confirm()

    def test_lot_propagation_multiple_lots_same_component_error(self):
        """Test lot propagation fails when component
        has reservations from multiple lots"""

        component_with_lot = self.product_tracked_by_lot
        component_with_lot2 = self.env["product.product"].create(
            {
                "name": "Test Component No Tracking",
                "type": "product",
                "tracking": "lot",
                "categ_id": component_with_lot.categ_id.id,
                "uom_id": component_with_lot.uom_id.id,
                "uom_po_id": component_with_lot.uom_po_id.id,
            }
        )

        final_product = self.env["product.product"].create(
            {
                "name": "Test Final Lot Product Multiple Lots Error",
                "type": "product",
                "tracking": "lot",
                "categ_id": component_with_lot.categ_id.id,
                "uom_id": component_with_lot.uom_id.id,
                "uom_po_id": component_with_lot.uom_po_id.id,
            }
        )

        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": final_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": component_with_lot.id,
                            "product_qty": 2.0,
                            "propagate_lot_number": True,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": component_with_lot2.id,
                            "product_qty": 1.0,
                            "propagate_lot_number": False,
                        },
                    ),
                ],
                "lot_number_propagation": True,
            }
        )

        mo = self.env["mrp.production"].create(
            {
                "product_id": final_product.id,
                "product_qty": 1.0,
                "bom_id": bom.id,
            }
        )

        location = self.env.ref("stock.stock_location_stock")

        lot_1 = self.env["stock.lot"].create(
            {
                "product_id": component_with_lot.id,
                "company_id": self.env.company.id,
                "name": self.LOT_NAME + "-1",
            }
        )
        self._update_qty_in_location(location, component_with_lot, 1, lot=lot_1)

        lot_2 = self.env["stock.lot"].create(
            {
                "product_id": component_with_lot.id,
                "company_id": self.env.company.id,
                "name": self.LOT_NAME + "-2",
            }
        )
        self._update_qty_in_location(location, component_with_lot, 1, lot=lot_2)

        lot_3 = self.env["stock.lot"].create(
            {
                "product_id": component_with_lot2.id,
                "company_id": self.env.company.id,
                "name": self.LOT_NAME + "-3",
            }
        )
        self._update_qty_in_location(location, component_with_lot2, 1, lot=lot_3)

        mo.action_confirm()
        self.assertTrue(mo.is_lot_number_propagated)

        mo.action_assign()

        move_with_lot = mo._get_propagating_component_move()
        reserved_lots = move_with_lot.move_line_ids.mapped("lot_id")
        self.assertEqual(len(reserved_lots), 2)

        self.assertFalse(mo._can_propagate_lot_number())

        self._set_qty_done(mo)

        with self.assertRaises(UserError):
            mo.button_mark_done()
