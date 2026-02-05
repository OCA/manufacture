# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestMrpSubcontractingAutoCreateLot(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.subcontractor = cls.env["res.partner"].create({"name": "Subcontractor"})

        cls.tracked_auto_product = cls.env["product.product"].create(
            {
                "name": "Tracked Auto Lot Product",
                "type": "product",
                "tracking": "lot",
                "auto_create_lot": True,
            }
        )

        cls.tracked_no_auto_product = cls.env["product.product"].create(
            {
                "name": "Tracked No Auto Lot Product",
                "type": "product",
                "tracking": "lot",
                "auto_create_lot": False,
            }
        )

        cls.untracked_product = cls.env["product.product"].create(
            {
                "name": "Untracked Product",
                "type": "product",
                "tracking": "none",
            }
        )

    def _create_mo(self, product, qty=1.0, is_subcontracted=True):
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_id": product.id,
                "product_qty": 1.0,
                "type": "normal" if not is_subcontracted else "subcontract",
                "subcontractor_ids": [self.subcontractor.id]
                if is_subcontracted
                else [],
            }
        )

        mo = self.env["mrp.production"].create(
            {
                "product_id": product.id,
                "product_qty": 1.0,
                "bom_id": bom.id,
            }
        )
        mo.action_confirm()
        mo.qty_producing = qty
        if is_subcontracted:
            # Force the move dest
            move = self.env["stock.move"].create(
                {
                    "product_id": product.id,
                    "product_uom_qty": qty,
                    "product_uom": product.uom_id.id,
                    "location_id": self.env.ref("stock.stock_location_suppliers").id,
                    "location_dest_id": self.env.ref("stock.stock_location_stock").id,
                    "production_id": mo.id,
                    "is_subcontract": True,
                }
            )
            mo.move_finished_ids.move_dest_ids = [move.id]
        return mo

    def test_lot_created_when_all_conditions_met(self):
        """Lot is auto-created for subcontracting MO when all conditions match.
        That is, the product is tracked, it has the create auto lot option set,
        qty has been produced and it is a subcontracted MO"""
        mo = self._create_mo(self.tracked_auto_product, is_subcontracted=True)
        mo.subcontracting_record_component()
        self.assertTrue(mo.lot_producing_id)

    def test_no_lot_for_untracked_product(self):
        """No lot is created for untracked products."""
        mo = self._create_mo(self.untracked_product, is_subcontracted=True)
        mo.subcontracting_record_component()
        self.assertFalse(mo.lot_producing_id)

    def test_no_lot_when_auto_create_lot_disabled(self):
        """No lot is created when auto_create_lot is False."""
        mo = self._create_mo(self.tracked_no_auto_product, is_subcontracted=True)
        mo.subcontracting_record_component()
        self.assertFalse(mo.lot_producing_id)

    def test_no_lot_when_qty_producing_zero(self):
        """No lot is created if qty_producing is zero."""
        mo = self._create_mo(self.tracked_auto_product, qty=0, is_subcontracted=True)
        mo.subcontracting_record_component()
        self.assertFalse(mo.lot_producing_id)

    def test_no_lot_without_subcontract_move(self):
        """No lot is created if there is no subcontract move."""
        mo = self._create_mo(self.tracked_auto_product, is_subcontracted=False)
        with self.assertRaises(UserError):
            mo.subcontracting_record_component()
            self.assertFalse(mo.lot_producing_id)
