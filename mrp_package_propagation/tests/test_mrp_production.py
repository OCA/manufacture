# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

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
        with Form(cls.env["mrp.production"]) as form:
            form.bom_id = cls.bom
            cls.order = form.save()

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
