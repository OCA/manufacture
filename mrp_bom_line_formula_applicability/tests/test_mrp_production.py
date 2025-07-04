#  Copyright 2024 Simone Rubino - Aion Tech
#  Copyright 2025 ForgeFlow
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import first

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestMRPProduction(TestMrpCommon):
    def test_line_applicability(self):
        """When a BoM line has a formula for the applicability,
        the formula computes the applicability of the generated production order line.
        If the formula evaluates to False, the line is not included
        in the production order.
        """
        # Arrange
        formula_applicability = False
        bom = self.bom_1.copy()
        formula_bom_line = first(bom.bom_line_ids)
        formula_bom_line["applicability_formula"] = (
            f"applicable = {formula_applicability}"
        )
        # Act
        order = self.env["mrp.production"].create(
            {
                "bom_id": bom.id,
            }
        )

        # Assert
        formula_order_line = order.move_raw_ids.filtered(
            lambda ol: ol.bom_line_id == formula_bom_line
        )
        self.assertFalse(formula_order_line)
