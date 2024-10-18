# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError
from odoo.tests.common import Form

from .common import Common


class TestMrpBom(Common):
    def test_bom_display_lot_number_propagation(self):
        self.assertTrue(self.bom.display_lot_number_propagation)
        self.bom.product_tmpl_id.tracking = "none"
        self.assertFalse(self.bom.display_lot_number_propagation)

    def test_bom_line_check_propagate_lot_number_not_tracked(self):
        form = Form(self.bom)
        form.lot_number_propagation = True
        # Flag a line that can't be propagated
        line_form = form.bom_line_ids.edit(2)  # line without tracking
        line_form.propagate_lot_number = True
        line_form.save()
        with self.assertRaisesRegex(ValidationError, "Only components tracked"):
            form.save()

    def test_bom_line_check_propagate_lot_number_tracked_by_lot(self):
        form = Form(self.bom)
        form.lot_number_propagation = True
        # Flag a line tracked by lot (not SN) which is not supported
        line_form = form.bom_line_ids.edit(1)
        line_form.propagate_lot_number = True
        line_form.save()
        with self.assertRaisesRegex(ValidationError, "Only components tracked"):
            form.save()

    def test_bom_line_check_propagate_lot_number_same_tracking(self):
        form = Form(self.bom)
        form.lot_number_propagation = True
        # Flag a line whose tracking type is the same than the finished product
        line_form = form.bom_line_ids.edit(0)
        line_form.propagate_lot_number = True
        line_form.save()
        form.save()

    def test_bom_check_propagate_lot_number(self):
        # Configure the BoM to propagate the lot/SN without enabling any line
        with self.assertRaisesRegex(ValidationError, "a line has to be configured"):
            self.bom.lot_number_propagation = True

    def test_reset_tracking_on_bom_product(self):
        # Configure the BoM to propagate the lot/SN
        with Form(self.bom) as form:
            form.lot_number_propagation = True
            line_form = form.bom_line_ids.edit(0)  # Line tracked by SN
            line_form.propagate_lot_number = True
            line_form.save()
            form.save()
        # Reset the tracking on the finished product
        with self.assertRaisesRegex(ValidationError, "A BoM propagating"):
            self.bom.product_tmpl_id.tracking = "none"

    def test_reset_tracking_on_bom_component(self):
        # Configure the BoM to propagate the lot/SN
        with Form(self.bom) as form:
            form.lot_number_propagation = True
            line_form = form.bom_line_ids.edit(0)  # Line tracked by SN
            line_form.propagate_lot_number = True
            line_form.save()
            form.save()
        # Reset the tracking on the component which propagates the SN
        with self.assertRaisesRegex(ValidationError, "This component is"):
            self.line_tracked_by_sn.product_id.tracking = "none"
