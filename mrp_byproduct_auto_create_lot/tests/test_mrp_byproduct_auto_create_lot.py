# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged

from .common import CommonMrpByproductAutoCreateLot


@tagged("post_install", "-at_install")
class TestMrpByproductAutoLot(CommonMrpByproductAutoCreateLot, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create 3 products with lot/serial and auto_create True/False
        cls.product_b = cls._create_product()
        cls.product_serial = cls._create_product(tracking="serial")
        cls.product_a = cls._create_product(tracking="none")
        cls.product_serial_not_auto = cls._create_product(tracking="serial", auto=False)

        cls.bom = cls._create_bom(
            product=cls.product_manuf.id, by_product=cls.product_b
        )
        cls.bom_no_tracked_byproduct = cls._create_bom(
            product=cls.product_manuf.id, by_product=cls.product_a
        )
        cls.bom_serial_tracked_byproduct = cls._create_bom(
            product=cls.product_manuf.id, by_product=cls.product_serial
        )
        cls.bom_serial_tracked_not_auto_byproduct = cls._create_bom(
            product=cls.product_manuf.id, by_product=cls.product_serial_not_auto
        )

    def test_01_manufacture_byproduct_auto_create_lot(self):
        """Test that a lot number is automatically created for the by-product"""
        self.production = self._create_manufacturing_order(bom=self.bom)
        self.production.action_confirm()
        self.production.button_plan()
        self.production.qty_producing = 1.0
        self.production.button_mark_done()

        # Check if a lot number was created and assigned to the by-product move line
        byproduct_move_line = self.production.move_byproduct_ids.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_b
        )
        self.assertTrue(
            byproduct_move_line.lot_id, "Lot number not created for by-product"
        )

    def test_02_no_lot_for_untracked_product(self):
        """Test that no lot is created for a by-product without tracking"""
        self.production = self._create_manufacturing_order(
            bom=self.bom_no_tracked_byproduct
        )
        self.production.action_confirm()
        self.production.button_plan()
        self.production.qty_producing = 1.0
        self.production.button_mark_done()

        byproduct_move_line = self.production.move_byproduct_ids.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_a
        )
        self.assertFalse(
            byproduct_move_line.lot_id, "Lot number created for untracked by-product"
        )

    def test_03_no_lot_if_already_assigned(self):
        """Test that no new lot is created if one is already assigned"""
        existing_lot = self.env["stock.lot"].create(
            {
                "name": "Existing Lot",
                "product_id": self.product_b.id,
            }
        )
        self.production = self._create_manufacturing_order(bom=self.bom)
        self.production.action_confirm()
        self.production.button_plan()
        byproduct_move_line = self.production.move_byproduct_ids.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_b
        )
        byproduct_move_line.lot_id = existing_lot
        self.production.button_mark_done()
        self.assertEqual(
            byproduct_move_line.lot_id,
            existing_lot,
            "New lot created when one was already assigned",
        )

    def test_04_no_lot_for_zero_qty_byproduct(self):
        """Test that no lot is created for a zero qty produced by-product"""
        self.production = self._create_manufacturing_order(
            bom=self.bom, by_product_qty=0.0
        )
        self.production.action_confirm()
        self.production.button_plan()
        self.production.button_mark_done()

        byproduct_move_line = self.production.move_byproduct_ids.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_b
        )
        self.assertFalse(
            byproduct_move_line.lot_id, "Lot number created for untracked by-product"
        )

    def test_05_manufacture_byproduct_auto_create_lot_serial(self):
        """Test that a serial number is automatically created for the by-product"""
        self.production = self._create_manufacturing_order(
            bom=self.bom_serial_tracked_byproduct, by_product_qty=2.0
        )
        self.production.action_confirm()
        self.production.button_plan()

        byproduct_move_line = self.production.move_byproduct_ids.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_serial
        )

        self.production.qty_producing = 1.0
        self.production.button_mark_done()
        self.assertTrue(
            byproduct_move_line.lot_id, "Serial number not created for by-product"
        )

        # Check if lots are unique per move and per product if managed
        # per serial
        move_lines_serial = self.production.move_byproduct_ids.move_line_ids.filtered(
            lambda m: m.product_id.tracking == "serial" and m.product_id.auto_create_lot
        )
        serials = []
        for move in move_lines_serial:
            serials.append(move.lot_id.name)
        self.assertUniqueIn(serials)

    def test_06_manual_auto_create_serial(self):
        self.production = self._create_manufacturing_order(
            bom=self.bom_serial_tracked_byproduct, by_product_qty=3.0
        )
        self.production.action_assign()
        # Check the display field
        move = self.production.move_byproduct_ids.filtered(
            lambda m: m.product_id == self.product_serial
        )
        self.assertFalse(move.display_assign_serial)
        self.production.button_plan()
        self.production.button_mark_done()

        self.production = self._create_manufacturing_order(
            bom=self.bom_serial_tracked_not_auto_byproduct, by_product_qty=1.0
        )
        self.production.button_plan()
        move = self.production.move_byproduct_ids.filtered(
            lambda m: m.product_id == self.product_serial_not_auto
        )
        self.assertTrue(move.display_assign_serial)

        # Test the exception if manual serials are not filled in
        with self.assertRaises(UserError), self.cr.savepoint():
            self.production.button_mark_done()

        # Assign manual serials
        self._assign_manual_serials(move)
        self.production.move_byproduct_ids.picked = True
        self.production.button_mark_done()
        serial = self.env["stock.lot"].search(
            [("product_id", "=", self.product_serial_not_auto.id)]
        )
        self.assertEqual(len(serial), 1)
        # Search for serials
        serial = self.env["stock.lot"].search(
            [("product_id", "=", self.product_serial.id)]
        )
        self.assertEqual(len(serial), 3)

    def _assign_manual_serials(self, moves):
        moves.move_line_ids.quantity = 1.0
        for line in moves.move_line_ids:
            line.lot_name = self.env["ir.sequence"].next_by_code("stock.lot.serial")

    def test_get_propagate_lot_setting(self):
        production = self._create_manufacturing_order(bom=self.bom)
        # Product setting takes precedence
        self.product_b.propagate_lot_to_byproduct = "yes"
        self.env.company.propagate_lot_to_byproduct = "no"
        self.assertEqual(production._get_propagate_lot_setting(self.product_b), "yes")
        self.product_b.propagate_lot_to_byproduct = "no"
        self.env.company.propagate_lot_to_byproduct = "yes"
        self.assertEqual(production._get_propagate_lot_setting(self.product_b), "no")
        # Falls back to company when product is empty
        self.product_b.propagate_lot_to_byproduct = False
        self.assertEqual(production._get_propagate_lot_setting(self.product_b), "yes")

    def test_propagate_lot_yes(self):
        self.env.company.propagate_lot_to_byproduct = "yes"
        bom = self._create_bom(
            by_product=self.product_b, main_product=self.product_manuf_tracked
        )
        production = self._create_manufacturing_order(
            bom=bom, product=self.product_manuf_tracked
        )
        production.action_confirm()
        production.button_plan()
        production.button_mark_done()
        self.assertTrue(production.lot_producing_id)
        byproduct_move_line = production.move_byproduct_ids.move_line_ids
        self.assertTrue(byproduct_move_line.lot_id)
        # Byproduct lot matches main product lot
        self.assertEqual(
            byproduct_move_line.lot_id.name, production.lot_producing_id.name
        )

    def test_propagate_lot_no(self):
        self.env.company.propagate_lot_to_byproduct = "no"
        bom = self._create_bom(
            by_product=self.product_b, main_product=self.product_manuf_tracked
        )
        production = self._create_manufacturing_order(
            bom=bom, product=self.product_manuf_tracked
        )
        production.action_confirm()
        production.button_plan()
        production.button_mark_done()
        self.assertTrue(production.lot_producing_id)
        byproduct_move_line = production.move_byproduct_ids.move_line_ids
        self.assertTrue(byproduct_move_line.lot_id)
        # Byproduct lot differs from main product lot
        self.assertNotEqual(
            byproduct_move_line.lot_id.name, production.lot_producing_id.name
        )
