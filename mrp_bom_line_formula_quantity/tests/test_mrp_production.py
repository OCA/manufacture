#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import first

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestMRPProduction(TestMrpCommon):
    def test_line_quantity(self):
        """When a BoM line has a formula for the quantity,
        the formula computes the quantity of the generated production order line.
        """
        # Arrange
        formula_quantity = 10
        bom = self.bom_1.copy()
        formula_bom_line = first(bom.bom_line_ids)
        formula_bom_line["quantity_formula"] = f"quantity = {formula_quantity}"
        # pre-condition
        self.assertNotEqual(formula_bom_line.product_qty, formula_quantity)

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
        self.assertEqual(formula_order_line.product_uom_qty, formula_quantity)
