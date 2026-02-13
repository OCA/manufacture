# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.exceptions import UserError
from odoo.tests import common, tagged

_logger = logging.getLogger(__name__)


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
        cls.ResPartner = cls.env["res.partner"]
        cls.StockPickingType = cls.env["stock.picking.type"]

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

        cls.picking_type = cls.StockPickingType.search(
            [
                ("code", "=", "mrp_operation"),
                ("warehouse_id.company_id", "=", cls.company.id),
            ],
            limit=1,
        )
        if not cls.picking_type:  # Fallback if no default MRP picking type
            warehouse = cls.env["stock.warehouse"].search(
                [("company_id", "=", cls.company.id)], limit=1
            )
            if not warehouse:
                warehouse = cls.env["stock.warehouse"].create(
                    {
                        "name": "Test Warehouse",
                        "code": "TWHMR",
                        "company_id": cls.company.id,
                    }
                )
            cls.picking_type = cls.StockPickingType.create(
                {
                    "name": "Test Manufacturing (for Merge)",
                    "code": "mrp_operation",
                    "warehouse_id": warehouse.id,
                    "sequence_code": "TMOMR",
                }
            )
        cls.picking_type.write({"owner_restriction": "picking_partner"})

        # Stock for the component: one quant without owner, one owned by cls.owner.
        quant_vals = {
            "product_id": cls.component.id,
            "location_id": cls.picking_type.default_location_src_id.id,
            "quantity": 250.00,
        }
        cls.env["stock.quant"].create(quant_vals)
        cls.env["stock.quant"].create(dict(quant_vals, owner_id=cls.owner.id))

    def _create_mo(self, product, bom, qty, owner=None, picking_type=None, origin=None):
        """Helper to create and confirm an MO."""
        vals = {
            "product_id": product.id,
            "bom_id": bom.id,
            "product_qty": qty,
            "product_uom_id": product.uom_id.id,
            "picking_type_id": (picking_type or self.picking_type).id,
        }
        if owner:
            vals["owner_id"] = owner.id
        if origin:
            vals["origin"] = origin
        mo = self.MrpProduction.create(vals)
        # MOs need to be confirmed to be eligible for merge in standard Odoo.
        mo.action_confirm()
        return mo

    def test_mrp_quant_assign_owner(self):
        self.assertEqual(self.component.qty_available, 250)
        self.component.invalidate_model(["qty_available"])
        self.assertEqual(
            self.component.with_context(skip_restricted_owner=True).qty_available, 500
        )
        mo = self.MrpProduction.create(
            {
                "product_id": self.finished_product.id,
                "bom_id": self.bom.id,
                "product_qty": 250,
                "picking_type_id": self.picking_type.id,
                "owner_id": self.owner.id,
            }
        )
        mo.action_confirm()
        mo.button_mark_done()

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

    def test_01_merge_mos_with_same_owner(self):
        """Merging MOs that share the same owner: the merged MO inherits it."""
        mo1_qty = 5.0
        mo2_qty = 3.0
        mo1 = self._create_mo(
            self.finished_product,
            self.bom,
            mo1_qty,
            owner=self.owner,
            origin="SO-MERGE-01-A",
        )
        mo2 = self._create_mo(
            self.finished_product,
            self.bom,
            mo2_qty,
            owner=self.owner,
            origin="SO-MERGE-01-B",
        )

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
        self.assertEqual(mo1.state, "cancel", "Original MO1 should be cancelled.")
        self.assertEqual(mo2.state, "cancel", "Original MO2 should be cancelled.")

    def test_02_merge_mos_with_different_owners(self):
        """Merging MOs with different owners: the merged MO gets no owner."""
        mo1 = self._create_mo(
            self.finished_product,
            self.bom,
            2.0,
            owner=self.owner,
            origin="SO-MERGE-02-A",
        )
        mo2 = self._create_mo(
            self.finished_product,
            self.bom,
            4.0,
            owner=self.owner2,
            origin="SO-MERGE-02-B",
        )

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
        mo1 = self._create_mo(
            self.finished_product,
            self.bom,
            1.0,
            owner=self.owner,
            origin="SO-MERGE-03-A",
        )
        mo2 = self._create_mo(
            self.finished_product, self.bom, 3.0, owner=None, origin="SO-MERGE-03-B"
        )

        action = (mo1 | mo2).action_merge()
        merged_mo = self.MrpProduction.browse(action.get("res_id"))

        self.assertFalse(
            merged_mo.owner_id,
            "Merged MO with mixed owner status should have no owner_id "
            "set by merge logic.",
        )
        self.assertEqual(mo1.state, "cancel")
        self.assertEqual(mo2.state, "cancel")

    def test_04_merge_mos_none_with_owner(self):
        """Merging MOs where none have an owner: the merged MO has no owner."""
        mo1 = self._create_mo(
            self.finished_product, self.bom, 2.5, owner=None, origin="SO-MERGE-04-A"
        )
        mo2 = self._create_mo(
            self.finished_product, self.bom, 2.5, owner=None, origin="SO-MERGE-04-B"
        )

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
        mo1 = self._create_mo(
            self.finished_product, self.bom, 7.0, owner=self.owner, origin="SO-MERGE-05"
        )

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
