# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError
from odoo.tests.common import Form

from .common import Common


class TestMrpBom(Common):
    def test_bom_display_package_propagation(self):
        self.assertTrue(self.bom.display_package_propagation)

    def test_bom_line_check_propagate_package_multi(self):
        form = Form(self.bom)
        form.package_propagation = True
        # Flag more than one line to propagate
        for i in range(len(form.bom_line_ids)):
            line_form = form.bom_line_ids.edit(i)
            line_form.propagate_package = True
            line_form.save()
        with self.assertRaisesRegex(ValidationError, "Only one component"):
            form.save()

    def test_bom_line_wrong_unit(self):
        form = Form(self.bom)
        form.package_propagation = True
        # Set the wrong UoM on the line
        line_form = form.bom_line_ids.edit(1)
        line_form.propagate_package = True
        line_form.product_uom_id = self.env.ref("uom.product_uom_dozen")
        line_form.save()
        with self.assertRaisesRegex(ValidationError, "The component propagating"):
            form.save()

    def test_bom_line_wrong_qty(self):
        form = Form(self.bom)
        form.package_propagation = True
        # Set the wrong qty on the line
        line_form = form.bom_line_ids.edit(1)
        line_form.propagate_package = True
        line_form.product_qty = 2
        line_form.save()
        with self.assertRaisesRegex(ValidationError, "The component propagating"):
            form.save()

    def test_bom_check_propagate_package(self):
        # Configure the BoM to propagate the package without enabling any line
        with self.assertRaisesRegex(ValidationError, "a line has to be configured"):
            self.bom.package_propagation = True
