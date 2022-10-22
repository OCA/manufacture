# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import UserError
from odoo.tests.common import Form

from .common import Common


class TestMrpProduction(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Configure the BoM to propagate lot number
        with Form(cls.bom) as form:
            form.lot_number_propagation = True
            line_form = form.bom_line_ids.edit(0)  # Line tracked by SN
            line_form.propagate_lot_number = True
            line_form.save()
            form.save()
        with Form(cls.env["mrp.production"]) as form:
            form.bom_id = cls.bom
            cls.order = form.save()

    def _set_qty_done(self, order):
        for line in order.move_raw_ids.move_line_ids:
            line.qty_done = line.product_uom_qty
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
            self.order.write({"lot_producing_id": False})

    def test_order_post_inventory(self):
        self._update_stock_component_qty(self.order)
        self.order.action_confirm()
        self._set_qty_done(self.order)
        self.order.button_mark_done()
        self.assertEqual(self.order.lot_producing_id.name, self.LOT_NAME)
