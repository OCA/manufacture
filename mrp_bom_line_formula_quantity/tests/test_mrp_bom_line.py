#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.fields import first

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestMRPBoMLine(TestMrpCommon):
    def test_formula_syntax_validation(self):
        """The formula of a BoM line is checked for invalid Python syntax."""
        # Arrange
        bom = self.bom_1.copy()
        bom_line = first(bom.bom_line_ids)

        # Act & Assert for an invalid syntax
        with self.assertRaises(ValidationError) as ve:
            bom_line.quantity_formula = "import *"
        self.assertIn("invalid syntax", ve.exception.args[0])

    def test_formula_runtime_validation(self):
        """The formula of a BoM line is checked for runtime errors."""
        # Arrange
        bom = self.bom_1.copy()
        bom_line = first(bom.bom_line_ids)

        # Act & Assert for an invalid function call (NameError)
        with self.assertRaises(ValidationError) as ve:
            bom_line.quantity_formula = (
                "quantity = math.nonexistent_function(product_uom_qty)"
            )
        self.assertIn("runtime error", ve.exception.args[0])
        self.assertIn(
            "object has no attribute 'nonexistent_function'", ve.exception.args[0]
        )

    def test_formula_valid(self):
        """The formula of a BoM line is correctly validated for a valid function."""
        # Arrange
        bom = self.bom_1.copy()
        bom_line = first(bom.bom_line_ids)

        # Act & Assert for a valid formula with math.ceil()
        try:
            bom_line.quantity_formula = "quantity = math.ceil(product_uom_qty)"
        except ValidationError:
            self.fail("Valid formula should not raise ValidationError")
