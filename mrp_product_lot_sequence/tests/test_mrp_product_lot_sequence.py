# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMrpProductLotSequence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_sequence = cls.env["ir.sequence"].create(
            {
                "name": "Test Product Lot Sequence",
                "implementation": "no_gap",
                "prefix": "TEST-",
                "padding": 4,
                "number_increment": 1,
                "use_date_range": False,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Manufactured Product",
                "detailed_type": "product",
                "tracking": "lot",
            }
        )
        cls.product.product_tmpl_id.lot_sequence_id = cls.product_sequence

    def _create_production(self):
        return self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1.0,
                "product_uom_id": self.product.uom_id.id,
            }
        )

    def test_product_policy_with_sequence(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "product_lot_sequence.policy",
            "product",
        )
        production = self._create_production()
        production.action_generate_serial()

        self.assertEqual(
            production.lot_producing_id.name,
            "TEST-0001",
        )
        production = self._create_production()
        production.action_generate_serial()
        self.assertEqual(
            production.lot_producing_id.name,
            "TEST-0002",
        )

    def test_product_policy_without_sequence(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "product_lot_sequence.policy",
            "product",
        )
        self.product.product_tmpl_id.lot_sequence_id = False
        production = self._create_production()
        production.action_generate_serial()
        self.assertTrue(production.lot_producing_id)
        self.assertTrue(production.lot_producing_id.name)

    def test_global_policy(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "product_lot_sequence.policy",
            "global",
        )
        production = self._create_production()
        production.action_generate_serial()
        self.assertTrue(production.lot_producing_id)
        self.assertTrue(production.lot_producing_id.name)
