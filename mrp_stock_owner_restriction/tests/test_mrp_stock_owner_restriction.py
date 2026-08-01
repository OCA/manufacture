# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestMrpStockOwnerRestriction(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.company = cls.env.ref("base.main_company")

        cls.Product = cls.env["product.product"]
        cls.MrpBom = cls.env["mrp.bom"]
        cls.MrpProduction = cls.env["mrp.production"]
        cls.MrpUnbuild = cls.env["mrp.unbuild"]
        cls.ResPartner = cls.env["res.partner"]
        cls.StockMove = cls.env["stock.move"]

        cls.finished_product = cls.Product.create(
            {
                "name": "Test Finished Product for Merge",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.component = cls.Product.create(
            {
                "name": "Test Component for Merge",
                "type": "consu",
                "is_storable": True,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.bom = cls.MrpBom.create(
            {
                "product_id": cls.finished_product.id,
                "product_tmpl_id": cls.finished_product.product_tmpl_id.id,
                "product_uom_id": cls.finished_product.uom_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )
        cls.env["mrp.bom.line"].create(
            {"bom_id": cls.bom.id, "product_id": cls.component.id, "product_qty": 1}
        )
        cls.owner = cls.ResPartner.create({"name": "Test Owner 1 (for Merge)"})
        cls.owner2 = cls.ResPartner.create({"name": "Test Owner 2 (for Merge)"})

        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        cls.picking_type = cls.warehouse.manu_type_id
        cls.picking_type.write({"owner_restriction": "picking_partner"})

        # Stock for the component: one quant without owner, one owned by cls.owner.
        quant_vals = {
            "product_id": cls.component.id,
            "location_id": cls.picking_type.default_location_src_id.id,
            "quantity": 250.00,
        }
        cls.env["stock.quant"].create(quant_vals)
        cls.env["stock.quant"].create(dict(quant_vals, owner_id=cls.owner.id))

    def _create_mo(self, qty, owner=None, origin=False):
        """Create and confirm an MO for the finished product."""
        mo = self.MrpProduction.create(
            {
                "product_id": self.finished_product.id,
                "bom_id": self.bom.id,
                "product_qty": qty,
                "product_uom_id": self.finished_product.uom_id.id,
                "picking_type_id": self.picking_type.id,
                "owner_id": owner.id if owner else False,
                "origin": origin,
            }
        )
        # MOs need to be confirmed to be eligible for merge in standard Odoo.
        mo.action_confirm()
        return mo

    def _produce(self, qty, owner=None, origin=False):
        """Create, confirm and complete an MO."""
        mo = self._create_mo(qty, owner=owner, origin=origin)
        mo.button_mark_done()
        return mo

    def _owned_component_qty(self, owner):
        """Component quantity sitting in stock under ``owner``."""
        quants = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.component.id),
                ("owner_id", "=", owner.id),
                ("location_id.usage", "=", "internal"),
            ]
        )
        return sum(quants.mapped("quantity"))

    def test_mrp_quant_assign_owner(self):
        self.assertEqual(self.component.qty_available, 250)
        self.component.invalidate_model(["qty_available"])
        self.assertEqual(
            self.component.with_context(skip_restricted_owner=True).qty_available, 500
        )
        mo = self._produce(250, owner=self.owner)

        # Check produced product owner and qty_available
        self.assertEqual(self.finished_product.qty_available, 0.00)
        self.finished_product.invalidate_model(["qty_available"])
        self.assertEqual(
            self.finished_product.with_context(
                skip_restricted_owner=True
            ).qty_available,
            250.00,
        )
        quant = self.env["stock.quant"].search(
            [("product_id", "=", self.finished_product.id)]
        )
        self.assertEqual(quant.owner_id, self.owner)

        # Confirm that component inventory with owner has been consumed
        self.assertEqual(self.component.qty_available, 250)
        self.component.invalidate_model(["qty_available"])
        self.assertEqual(
            self.component.with_context(skip_restricted_owner=True).qty_available, 250
        )

        # The finished move is deliberately left without a restricted owner, so
        # that it is not looked for in the internal location.
        self.assertFalse(mo.move_finished_ids.restricted_owner_id)

    def test_01_merge_mos_with_same_owner(self):
        """Merging MOs that share the same owner: the merged MO inherits it."""
        mo1_qty = 5.0
        mo2_qty = 3.0
        mo1 = self._create_mo(mo1_qty, owner=self.owner, origin="SO-MERGE-01-A")
        mo2 = self._create_mo(mo2_qty, owner=self.owner, origin="SO-MERGE-01-B")

        self.assertEqual(mo1.owner_id, self.owner)
        self.assertEqual(mo2.owner_id, self.owner)

        action = (mo1 | mo2).action_merge()
        merged_mo_id = action.get("res_id")
        self.assertTrue(
            merged_mo_id, "Merge action should return a res_id for the new MO."
        )
        merged_mo = self.MrpProduction.browse(merged_mo_id)

        self.assertEqual(
            merged_mo.owner_id,
            self.owner,
            "Merged MO should inherit the common owner_id.",
        )
        self.assertEqual(
            merged_mo.product_qty,
            mo1_qty + mo2_qty,
            "Merged MO quantity should be the sum.",
        )
        # The owner is set before the merged MO reserves, so the components are
        # taken from the owner's stock.
        self.assertEqual(merged_mo.move_raw_ids.move_line_ids.owner_id, self.owner)
        self.assertEqual(mo1.state, "cancel", "Original MO1 should be cancelled.")
        self.assertEqual(mo2.state, "cancel", "Original MO2 should be cancelled.")

    def test_02_merge_mos_with_different_owners(self):
        """Merging MOs with different owners: the merged MO gets no owner."""
        mo1 = self._create_mo(2.0, owner=self.owner, origin="SO-MERGE-02-A")
        mo2 = self._create_mo(4.0, owner=self.owner2, origin="SO-MERGE-02-B")

        action = (mo1 | mo2).action_merge()
        merged_mo = self.MrpProduction.browse(action.get("res_id"))

        self.assertFalse(
            merged_mo.owner_id,
            "Merged MO with different owners should have no owner_id "
            "set by merge logic.",
        )
        self.assertEqual(mo1.state, "cancel")
        self.assertEqual(mo2.state, "cancel")

    def test_03_merge_mos_one_with_owner_one_without(self):
        """Merging MOs with mixed owner status: the merged MO gets no owner."""
        mo1 = self._create_mo(1.0, owner=self.owner, origin="SO-MERGE-03-A")
        mo2 = self._create_mo(3.0, origin="SO-MERGE-03-B")

        action = (mo1 | mo2).action_merge()
        merged_mo = self.MrpProduction.browse(action.get("res_id"))

        self.assertFalse(
            merged_mo.owner_id,
            "Merged MO with mixed owner status should have no owner_id "
            "set by merge logic.",
        )
        self.assertEqual(mo1.state, "cancel")
        self.assertEqual(mo2.state, "cancel")

    def test_03b_merge_mos_first_without_owner(self):
        """The order of the MOs does not matter for the mixed owner case."""
        mo1 = self._create_mo(1.0, origin="SO-MERGE-03B-A")
        mo2 = self._create_mo(3.0, owner=self.owner, origin="SO-MERGE-03B-B")

        action = (mo1 | mo2).action_merge()
        merged_mo = self.MrpProduction.browse(action.get("res_id"))

        self.assertFalse(merged_mo.owner_id)

    def test_04_merge_mos_none_with_owner(self):
        """Merging MOs where none have an owner: the merged MO has no owner."""
        mo1 = self._create_mo(2.5, origin="SO-MERGE-04-A")
        mo2 = self._create_mo(2.5, origin="SO-MERGE-04-B")

        action = (mo1 | mo2).action_merge()
        merged_mo = self.MrpProduction.browse(action.get("res_id"))

        self.assertFalse(
            merged_mo.owner_id,
            "Merged MO from sources without an owner should have no owner_id.",
        )
        self.assertEqual(mo1.state, "cancel")
        self.assertEqual(mo2.state, "cancel")

    def test_05_merge_single_mo_raises_error(self):
        """'Merging' a single MO raises UserError and leaves it untouched."""
        mo1 = self._create_mo(7.0, owner=self.owner, origin="SO-MERGE-05")

        with self.assertRaises(UserError):
            mo1.action_merge()

        self.assertEqual(
            mo1.owner_id,
            self.owner,
            "Owner should remain on single MO after failed merge attempt.",
        )
        self.assertNotEqual(
            mo1.state,
            "cancel",
            "Single MO should not be cancelled on failed merge attempt.",
        )

    def test_06_setting_owner_releases_the_reservation(self):
        """Assigning an owner drops reservations made for the previous one."""
        mo = self._create_mo(5.0, origin="SO-OWNER-06")
        self.assertTrue(mo.move_raw_ids.move_line_ids)
        self.assertFalse(mo.move_raw_ids.move_line_ids.owner_id)

        mo.owner_id = self.owner
        self.assertFalse(
            mo.move_raw_ids.move_line_ids,
            "Reservation on unowned stock should be released.",
        )

        mo.action_assign()
        self.assertEqual(
            mo.move_raw_ids.move_line_ids.owner_id,
            self.owner,
            "Components should be reserved again from the owner's stock.",
        )
        self.assertEqual(mo.move_raw_ids.restricted_owner_id, self.owner)

    def test_07_unbuild_mo_with_owner(self):
        """Unbuilding an owned MO returns the components to that owner."""
        mo = self._produce(5.0, owner=self.owner, origin="SO-UNBUILD-07")
        unbuild = self.MrpUnbuild.create({"mo_id": mo.id, "product_qty": 5.0})

        unbuild.action_validate()

        self.assertEqual(
            unbuild.state, "done", "The owned finished product should be unbuildable."
        )
        # The moves of the unbuild are restricted to the owner of the MO they undo.
        moves = unbuild.produce_line_ids
        self.assertTrue(moves)
        self.assertEqual(moves.restricted_owner_id, self.owner)
        self.assertEqual(moves.move_line_ids.owner_id, self.owner)
        # The components are back in the owner's stock.
        self.assertEqual(self._owned_component_qty(self.owner), 250)

    def test_08_unbuild_mo_without_owner(self):
        """Unbuilding an MO without an owner keeps standard behaviour."""
        mo = self._produce(5.0, origin="SO-UNBUILD-08")
        unbuild = self.MrpUnbuild.create({"mo_id": mo.id, "product_qty": 5.0})

        unbuild.action_validate()

        self.assertEqual(unbuild.state, "done")
        moves = unbuild.produce_line_ids
        self.assertTrue(moves)
        self.assertFalse(moves.restricted_owner_id)
        self.assertFalse(moves.move_line_ids.owner_id)

    def test_09_owner_for_assign_on_chained_and_unrelated_moves(self):
        """A move feeding a component move follows the owner of its MO."""
        mo = self._create_mo(2.0, owner=self.owner, origin="SO-CHAIN-09")
        move_vals = {
            "name": "Feed the component move",
            "product_id": self.component.id,
            "product_uom_qty": 2.0,
            "product_uom": self.component.uom_id.id,
            "location_id": self.warehouse.wh_input_stock_loc_id.id,
            "location_dest_id": self.warehouse.lot_stock_id.id,
        }
        origin_move = self.StockMove.create(
            dict(move_vals, move_dest_ids=[Command.set(mo.move_raw_ids.ids)])
        )
        self.assertEqual(origin_move._get_owner_for_assign(), self.owner)
        self.assertEqual(origin_move.restricted_owner_id, self.owner)

        # A move unrelated to manufacturing falls back on the base module.
        unrelated_move = self.StockMove.create(move_vals)
        self.assertFalse(unrelated_move._get_owner_for_assign())
        self.assertFalse(unrelated_move.restricted_owner_id)
