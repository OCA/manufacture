# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError

from .common import Common


class TestMrpBom(Common):
    def test_bom_display_lot_number_propagation(self):
        self.assertTrue(self.bom.display_lot_number_propagation)
        self.bom.product_tmpl_id.tracking = "none"
        self.assertFalse(self.bom.display_lot_number_propagation)

    def test_bom_line_check_propagate_lot_number_multi(self):
        self.bom.lot_number_propagation = True
        # Flag more than one line to propagate
        with self.assertRaisesRegex(ValidationError, "Only one BoM"):
            self.bom.bom_line_ids.write({"propagate_lot_number": True})

    def test_bom_line_check_propagate_lot_number_not_tracked(self):
        self.bom.lot_number_propagation = True
        # Flag a line that can't be propagated
        with self.assertRaisesRegex(ValidationError, "Only components tracked"):
            self.line_no_tracking.propagate_lot_number = True

    def test_bom_line_check_propagate_lot_number_tracked_by_lot(self):
        self.bom.lot_number_propagation = True
        # Flag a line tracked by lot (not SN) which is not supported
        with self.assertRaisesRegex(ValidationError, "Only components tracked"):
            self.line_tracked_by_lot.propagate_lot_number = True

    def test_bom_line_check_propagate_lot_number_same_tracking(self):
        self.bom.lot_number_propagation = True
        # Flag a line whose tracking type is the same than the finished product
        self.line_tracked_by_sn.propagate_lot_number = True
