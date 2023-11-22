# Copyright 2023 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestMrpProduction(TestMrpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mo = cls.generate_mo(qty_final=1)[0]
        for line in cls.mo.move_raw_ids:
            cls.env["stock.quant"]._update_available_quantity(
                line.product_id, cls.mo.picking_type_id.default_location_src_id, 10.0
            )

    def test_compute_action_operation_auto_fill_allowed(self):
        # The auto fill action isn't available when mo is in confirm
        # state.
        self.assertEqual(self.mo.state, "confirmed")
        self.assertFalse(self.mo.action_op_auto_fill_allowed)

        # The auto fill action is available when should_consume_qty is set.
        self.mo.qty_producing = 1
        self.assertTrue(self.mo.action_op_auto_fill_allowed)

    def test_action_operation_auto_fill(self):
        self.mo.qty_producing = 1.0
        self.mo.action_assign()
        self.assertEqual(self.mo.state, "to_close")
        self.mo.action_operation_auto_fill()
        check_auto_fill = all(
            line.should_consume_qty == line.quantity_done
            for line in self.mo.move_raw_ids
        )
        self.assertTrue(
            check_auto_fill,
            "Not all move_raw_ids lines have equal product_uom_qty and quantity_done",
        )
