# Copyright 2026 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMrpBomWarnMessage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create the MRP BOM with a warning and its needed dataa
        cls.product_uom = cls.env.ref("uom.product_uom_unit")
        cls.product_to_build = cls.env["product.product"].create(
            {
                "name": "Young Tom",
                "type": "consu",
            }
        )
        cls.product_to_use_1 = cls.env["product.product"].create(
            {
                "name": "Botox",
                "type": "consu",
            }
        )
        cls.warn_message = "Warning! Your review is being too good"
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_id": cls.product_to_build.id,
                "product_tmpl_id": cls.product_to_build.product_tmpl_id.id,
                "product_uom_id": cls.product_uom.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.product_to_use_1.id, "product_qty": 1})
                ],
                "production_warn": "warning",
                "production_warn_msg": cls.warn_message,
            }
        )

    def _create_mrp_production(self):
        return self.env["mrp.production"].create(
            {
                "product_id": self.product_to_build.id,
                "product_qty": 1,
                "product_uom_id": self.product_uom.id,
                "bom_id": self.bom.id,
            }
        )

    def test_compute_warn_message(self):
        """Check that the warn is correctly displayed in the mrp production"""
        # Create mrp production and check that the warn is computed
        production_order1 = self._create_mrp_production()
        self.assertIn(self.warn_message, production_order1.production_warn_msg)
        # Remove the warning from bom and check that the removal is propagated
        self.bom.write(
            {
                "production_warn": "no-message",
            }
        )
        self.assertFalse(production_order1.production_warn_msg)

        # Create a cancelled mrp production and check that the warn is not computed
        production_order2 = self._create_mrp_production()
        production_order2.write({"state": "cancel"})
        self.assertFalse(production_order2.production_warn_msg)

    def test_onchange_warn_message(self):
        """Check that the onchange returns a warning"""
        production_order = self._create_mrp_production()
        warn = production_order._onchange_bom_id_warning()
        self.assertEqual(dict, type(warn))
        self.assertIn(self.warn_message, warn.get("warning", {}).get("message"))
