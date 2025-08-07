# Copyright 2025 Studio73 - Eugenio Micó <eugenio@studio73.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TestMrpBomAttributeMatchBase


class TestMrpBomLine(TestMrpBomAttributeMatchBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")
        cls.product_plastic.write(
            {
                "uom_id": cls.uom_dozen.id,
                "uom_po_id": cls.uom_dozen.id,
            }
        )

    def test_bom_line_create_with_component_template(self):
        bom_line = self.env["mrp.bom.line"].create(
            {
                "bom_id": self.bom_id.id,
                "component_template_id": self.product_plastic.id,
                "product_qty": 1.0,
            }
        )
        self.assertEqual(bom_line.product_uom_id.id, self.product_plastic.uom_id.id)
        self.assertEqual(bom_line.product_uom_id.id, self.uom_dozen.id)

    def test_bom_line_create_with_custom_uom(self):
        """Prove that product_uom_id does not change when it is already specified."""
        bom_line = self.env["mrp.bom.line"].create(
            {
                "bom_id": self.bom_id.id,
                "component_template_id": self.product_plastic.id,
                "product_uom_id": self.uom_unit.id,  # UdM explícita
                "product_qty": 1.0,
            }
        )
        self.assertEqual(bom_line.product_uom_id.id, self.uom_unit.id)
        self.assertNotEqual(bom_line.product_uom_id.id, self.product_plastic.uom_id.id)

    def test_bom_line_create_with_product_id(self):
        """
        Prove that product_uom_id is not set from the template when product_id exists.
        """
        plastic_variant = self.product_plastic.product_variant_ids[0]
        bom_line = self.env["mrp.bom.line"].create(
            {
                "bom_id": self.bom_id.id,
                "product_id": plastic_variant.id,
                "component_template_id": self.product_plastic.id,
                "product_qty": 1.0,
            }
        )
        self.assertEqual(bom_line.product_uom_id.id, plastic_variant.uom_id.id)
