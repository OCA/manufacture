# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import random
import string

from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests import Form

from .common import Common


class TestMrpProduction(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Configure the BoM to propagate lot number
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

    def test_order_write_lot_producing_id_not_allowed(self):
        with self.assertRaisesRegex(UserError, "not allowed"):
            self.order.write({"lot_producing_id": "test"})

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

    def test_mass_produce_wizard(self):
        order = self._create_order(self.bom_product_product, self.bom, qty=5)
        self._update_stock_component_qty(order)
        order.action_confirm()
        tracked_moves = order.move_raw_ids.filtered(
            lambda mv: mv.product_id.tracking != "none"
        )
        self.assertTrue(len(tracked_moves) > 1)
        res = order.button_mark_done()
        self.assertEqual(type(res), dict)
        self.assertEqual(res["res_model"], "mrp.batch.produce")

        propagate_move = order._get_propagating_component_move()
        propagate_move_lines = propagate_move.move_line_ids
        component_lot_name = (tracked_moves - propagate_move).move_line_ids.lot_id.name

        wizard_form = Form(self.env["mrp.batch.produce"].with_context(**res["context"]))

        # Executing wizard without entering same name for finished product and
        #  propagated component must raise an error
        def random_name():
            return "".join(random.choice(string.ascii_lowercase) for i in range(10))

        wizard_form.production_text = "\n".join(
            [
                f"{random_name()},{comp_serial_name},{component_lot_name}"
                for comp_serial_name in propagate_move_lines.lot_id.mapped("name")
            ]
        )
        wizard = wizard_form.save()
        with self.assertRaisesRegex(
            UserError, "set to propagate lot number from component"
        ):
            wizard.action_done()
        wizard_form = Form(wizard)
        wizard_form.production_text = "\n".join(
            [
                f"{comp_serial_name},{comp_serial_name},{component_lot_name}"
                for comp_serial_name in propagate_move_lines.lot_id.mapped("name")
            ]
        )
        wizard = wizard_form.save()
        wizard.action_done()

        self.assertEqual(order.state, "done")
        for backorder in order.procurement_group_id.mrp_production_ids:
            propagating_move = backorder._get_propagating_component_move()
            self.assertEqual(
                backorder.lot_producing_id.name,
                propagating_move.move_line_ids.lot_id.name,
            )

    def test_mass_produce(self):
        order = self._create_order(
            self.finished_propagated_product, self.propagate_bom, qty=5
        )
        # Init component stock
        for i in range(5):
            lot = self.env["stock.lot"].create(
                {
                    "name": "SN-000%d" % i,
                    "product_id": self.component_propagated_product.id,
                }
            )
            self.env["stock.quant"]._update_available_quantity(
                self.component_propagated_product,
                self.stock_location,
                quantity=1.0,
                lot_id=lot,
            )
        order.action_confirm()
        components_serials = order.move_raw_ids.filtered("propagate_lot_number").mapped(
            "move_line_ids.lot_id"
        )
        self.assertEqual(len(components_serials), 5)
        batch_propagate_action = order.button_mark_done()
        wiz = (
            self.env[batch_propagate_action["res_model"]]
            .with_context(**batch_propagate_action["context"])
            .create({})
        )
        wiz.action_done()
        self.assertEqual(order.state, "done")
        for backorder in order.procurement_group_id.mrp_production_ids:
            propagating_move = backorder._get_propagating_component_move()
            self.assertEqual(
                backorder.lot_producing_id.name,
                propagating_move.move_line_ids.lot_id.name,
            )
