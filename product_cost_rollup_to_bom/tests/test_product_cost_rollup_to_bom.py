# Copyright 2026 Tessera - Abraham Anes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from unittest.mock import patch

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestProductCostRollupToBom(BaseCommon):
    @classmethod
    def _create_product(cls, name, price, categ):
        return cls.env["product.product"].create(
            {
                "name": name,
                "is_storable": True,
                "standard_price": price,
                "categ_id": categ.id,
            }
        )

    @classmethod
    def _create_bom(cls, product, uom, bom_type, lines):
        return cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_id": product.id,
                "product_qty": 1.0,
                "product_uom_id": uom.id,
                "type": bom_type,
                "bom_line_ids": [
                    Command.create({"product_id": comp.id, "product_qty": qty})
                    for comp, qty in lines
                ],
            }
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.unit = cls.env.ref("uom.product_uom_unit")
        cls.dozen = cls.env.ref("uom.product_uom_dozen")

        # Category using standard costing so the rollup applies.
        cls.categ = cls.env["product.category"].create(
            {
                "name": "Test Category",
                "property_cost_method": "standard",
                "property_valuation": "manual_periodic",
            }
        )

        # Product 1 is manufactured from Product 2..5.
        # Product 2 is itself manufactured from Product 6..9 (sub-assembly).
        cls.product_1 = cls._create_product("Product 1", 1000, cls.categ)
        cls.product_2 = cls._create_product("Product 2", 300, cls.categ)
        cls.product_3 = cls._create_product("Product 3", 10, cls.categ)
        cls.product_4 = cls._create_product("Product 4", 25, cls.categ)
        cls.product_5 = cls._create_product("Product 5", 100, cls.categ)
        cls.product_6 = cls._create_product("Product 6", 200, cls.categ)
        cls.product_7 = cls._create_product("Product 7", 10, cls.categ)
        cls.product_8 = cls._create_product("Product 8", 100, cls.categ)
        cls.product_9 = cls._create_product("Product 9", 25, cls.categ)

        # BoM for Product 1 (1 Unit):
        #   Product 2   1 Unit  (468.75 rolled up from its own BoM)
        #   Product 3   5 Unit *  10 =  50
        #   Product 4   4 Unit *  25 = 100
        #   Product 5   1 Unit * 100 = 100
        # Total rolled up = 468.75 + 50 + 100 + 100 = 718.75
        cls.bom_1 = cls._create_bom(
            cls.product_1,
            cls.unit,
            "normal",
            [
                (cls.product_2, 1),
                (cls.product_3, 5),
                (cls.product_4, 4),
                (cls.product_5, 1),
            ],
        )

        # BoM for Product 2 (1 Dozen):
        #   Product 6   12 * 200 = 2400
        #   Product 7   60 *  10 =  600
        #   Product 8   12 * 100 = 1200
        #   Product 9   57 *  25 = 1425
        # Total per dozen = 5625 -> per unit = 468.75
        cls.bom_2 = cls._create_bom(
            cls.product_2,
            cls.dozen,
            "phantom",
            [
                (cls.product_6, 12),
                (cls.product_7, 60),
                (cls.product_8, 12),
                (cls.product_9, 57),
            ],
        )

    def test_button_bom_cost_rolls_up_recursively(self):
        """button_bom_cost rolls the child BoM cost up into the sub-assembly."""
        self.product_1.button_bom_cost()
        # The sub-assembly standard price is updated from its own BoM.
        self.assertAlmostEqual(self.product_2.standard_price, 468.75, places=2)
        # The finished product price uses the rolled-up sub-assembly cost.
        self.assertAlmostEqual(self.product_1.standard_price, 718.75, places=2)
        # Both the BoM and the recomputed sub-assembly are stamped.
        self.assertTrue(self.bom_1.std_cost_update_date)
        self.assertTrue(self.product_2.std_cost_update_date)

    def test_action_bom_cost_stamps_only_when_changed(self):
        """action_bom_cost updates the price and only stamps when it changes."""
        self.product_1.action_bom_cost()
        self.assertAlmostEqual(self.product_1.standard_price, 718.75, places=2)
        first_stamp = self.product_1.std_cost_update_date
        self.assertTrue(first_stamp)
        # Running it again without changes must not re-stamp the date.
        self.product_1.action_bom_cost()
        self.assertEqual(self.product_1.std_cost_update_date, first_stamp)

    def test_action_bom_cost_raises_on_fifo(self):
        """FIFO products cannot have their cost computed manually."""
        fifo_categ = self.env["product.category"].create(
            {
                "name": "FIFO Category",
                "property_cost_method": "fifo",
                "property_valuation": "manual_periodic",
            }
        )
        fifo_product = self._create_product("FIFO Product", 50, fifo_categ)
        with self.assertRaises(UserError):
            fifo_product.action_bom_cost()

    def test_compute_bom_cost_rollup(self):
        """The scheduler updates standard prices and notifies by email."""
        self.env.company.bom_cost_email = "rollup@example.com"
        with patch.object(
            type(self.env["mail.template"]), "send_mail"
        ) as mock_send_mail:
            self.env["mrp.bom"].compute_bom_cost_rollup()
        self.assertAlmostEqual(self.product_2.standard_price, 468.75, places=2)
        self.assertAlmostEqual(self.product_1.standard_price, 718.75, places=2)
        self.assertTrue(self.product_1.std_cost_update_date)
        mock_send_mail.assert_called()
