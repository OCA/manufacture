#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import first

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestMRPProduction(TestMrpCommon):
    def test_empty_bom_line(self):
        """When a BoM line has quantity 0,
        it does not generate a production order line.
        """
        # Arrange
        bom = self.bom_1
        empty_bom_line = first(bom.bom_line_ids)
        empty_bom_line["product_qty"] = 0
        # pre-condition
        self.assertFalse(empty_bom_line.product_qty)

        # Act
        order = self.env["mrp.production"].create(
            {
                "bom_id": bom.id,
            }
        )

        # Assert
        empty_order_line = order.move_raw_ids.filtered(
            lambda ol: ol.bom_line_id == empty_bom_line
        )
        self.assertFalse(empty_order_line)
