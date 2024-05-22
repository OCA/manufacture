# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import Form

from .common import Common


class TestMrpProduction(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Configure the BoM to propagate package
        with Form(cls.bom) as form:
            form.package_propagation = True
            line_form = form.bom_line_ids.edit(0)  # Line tracked by SN
            line_form.propagate_package = True
            line_form.save()
            form.save()
        cls.order = cls._create_manufacturing_order(cls.bom)

    @classmethod
    def _create_manufacturing_order(cls, bom):
        with Form(cls.env["mrp.production"]) as form:
            form.bom_id = bom
            return form.save()

    def _set_qty_done(self, order):
        for line in order.move_raw_ids.move_line_ids:
            line.qty_done = line.product_uom_qty
        order.qty_producing = order.product_qty

    def test_order_check_package_propagation(self):
        self.assertTrue(self.order.is_package_propagated)
        # Set a wrong quantity to produce
        self.order.product_qty = 2
        with self.assertRaisesRegex(UserError, "The BoM is propagating a package"):
            self.order.action_confirm()
        self.order.product_qty = self.order.bom_id.product_qty
        # Set a wrong UoM
        self.order.product_uom_id = self.env.ref("uom.product_uom_dozen")
        with self.assertRaisesRegex(UserError, "The BoM is propagating a package"):
            self.order.action_confirm()
        # Restore expected values to get the order validated
        self.order.product_uom_id = self.order.bom_id.product_uom_id
        self.order.product_qty = self.order.bom_id.product_qty
        self.order.action_confirm()

    def test_order_propagated_package_id(self):
        self.assertTrue(self.order.is_package_propagated)  # set by onchange
        self._update_stock_component_qty(self.order)
        self.order.action_confirm()
        self.order.action_assign()
        self.assertTrue(self.order.is_package_propagated)  # set by action_confirm
        self.assertTrue(any(self.order.move_raw_ids.mapped("propagate_package")))
        self._set_qty_done(self.order)
        self.assertEqual(self.order.propagated_package_id.name, self.PACKAGE_NAME)

    def test_order_post_inventory(self):
        self._update_stock_component_qty(self.order)
        self.order.action_confirm()
        self.order.action_assign()
        self._set_qty_done(self.order)
        self.order.action_generate_serial()
        self.order.button_mark_done()
        self.assertEqual(self.order.propagated_package_id.name, self.PACKAGE_NAME)
        self.assertEqual(
            self.order.move_finished_ids.move_line_ids.result_package_id.name,
            self.PACKAGE_NAME,
        )

    def test_order_propagated_package_id_through_consumable_component(self):
        """Test package propagation from a consumable component."""
        # NOTE: we enable the manufacturing in two steps in this test to get
        # ancestor moves (Pre-PICK transfer to validate to get components
        # available for MO) required to find the destination package among them.
        self.env.ref("stock.warehouse0").manufacture_steps = "pbm"
        # Enable the package propagation on a consumable component
        self.bom.bom_line_ids.propagate_package = False
        consu_bom_line = fields.first(
            self.bom.bom_line_ids.filtered(lambda o: o.product_id.type == "consu")
        )
        consu_bom_line.write({"product_qty": 1, "propagate_package": True})
        # Create MO
        order = self._create_manufacturing_order(self.bom)
        self.assertTrue(order.is_package_propagated)
        self._update_stock_component_qty(order)
        order.action_confirm()
        order.action_assign()
        order.picking_ids.action_assign()
        # Put a destination package in Pre-PICK for the consumable component
        consu_move_line = order.picking_ids.move_line_ids.filtered(
            lambda l: l.product_id == consu_bom_line.product_id
        )
        package = self.env["stock.quant.package"].create(
            {"name": self.PACKAGE_NAME + "-CONSU"}
        )
        consu_move_line.result_package_id = package
        # Validate the Pre-PICK: package is found by the MO
        for line in order.picking_ids.move_line_ids:
            line.qty_done = line.product_uom_qty
        order.picking_ids._action_done()
        self.assertTrue(order.is_package_propagated)
        self.assertTrue(any(order.move_raw_ids.mapped("propagate_package")))
        self.assertEqual(order.propagated_package_id, package)
        # Validate MO: package is propagated to finished product
        self._set_qty_done(order)
        order.action_generate_serial()
        order.button_mark_done()
        self.assertEqual(
            order.move_finished_ids.move_line_ids.result_package_id, package
        )
