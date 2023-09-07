# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestMrpProductionForceBom(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("mrp.product_product_computer_desk")
        cls.product_bom = cls.env.ref("mrp.mrp_bom_desk")
        cls.env["ir.config_parameter"].sudo().set_param(
            "mrp_production_force_bom.force_bom", "1"
        )
        # An additional product to simulate unexpected product
        cls.additional_product = cls.env["product.product"].create(
            {
                "name": "Additional Product",
                "type": "product",
            }
        )

    def test_mrp_production_without_bom(self):
        """Test MO without setting a BOM."""
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "product_uom_id": self.product.uom_id.id,
            }
        )
        with self.assertRaises(ValidationError):
            mo.action_confirm()

    def test_mrp_production_missing_product(self):
        """Test MO with a missing product from the BOM."""
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.product_bom.id,
                "product_uom_id": self.product.uom_id.id,
            }
        )
        # Remove one product from raw materials to simulate missing product scenario
        mo.move_raw_ids = mo.move_raw_ids[:-1]
        with self.assertRaises(ValidationError):
            mo.action_confirm()

    def test_mrp_production_unexpected_product(self):
        """Test MO with an unexpected product not in the BOM."""
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.product_bom.id,
                "product_uom_id": self.product.uom_id.id,
            }
        )
        # Add an additional unexpected product to raw materials
        self.env["stock.move"].create(
            {
                "name": "Unexpected Move",
                "product_id": self.additional_product.id,
                "product_uom": self.additional_product.uom_id.id,
                "product_uom_qty": 1.0,
                "location_id": mo.location_src_id.id,
                "location_dest_id": mo.product_id.property_stock_production.id,
                "raw_material_production_id": mo.id,
            }
        )
        with self.assertRaises(ValidationError):
            mo.action_confirm()
