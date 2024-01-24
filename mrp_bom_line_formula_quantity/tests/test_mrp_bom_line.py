#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.fields import first

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestMRPBoMLine(TestMrpCommon):
    def test_formula_validation(self):
        """The formula of a BoM line is checked for not permitted operations."""
        # Arrange
        bom = self.bom_1.copy()
        bom_line = first(bom.bom_line_ids)

        # Act
        with self.assertRaises(ValidationError) as ve:
            bom_line["quantity_formula"] = "import *"
        exc_message = ve.exception.args[0]

        # Assert
        self.assertIn("invalid syntax", exc_message)
