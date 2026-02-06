# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestMrpBomLineUomRounding(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_unit.rounding = 1.0
        cls.product_finished = cls.env["product.product"].create(
            {"name": "Finished Product", "type": "consu"}
        )
        cls.product_component = cls.env["product.product"].create(
            {"name": "Component", "type": "consu", "uom_id": cls.uom_unit.id}
        )

    def _create_bom_line(self, qty):
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product_finished.product_tmpl_id.id,
                "product_qty": 1.0,
            }
        )
        return self.env["mrp.bom.line"].create(
            {
                "bom_id": bom.id,
                "product_id": self.product_component.id,
                "product_qty": qty,
            }
        )

    def test_invalid_quantity_rejected_on_create(self):
        with self.assertRaises(ValidationError) as cm:
            self._create_bom_line(0.1)
        self.assertIn("rounding precision", str(cm.exception))

    def test_invalid_quantity_rejected_on_write(self):
        line = self._create_bom_line(2.0)
        self.assertEqual(line.product_qty, 2.0)
        with self.assertRaises(ValidationError):
            line.product_qty = 0.5
