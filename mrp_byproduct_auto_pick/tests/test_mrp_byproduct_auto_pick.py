# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form, TransactionCase


class TestMrpByproductAutoPick(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        manufacture_route = cls.env.ref("mrp.route_warehouse0_manufacture")
        cls.finished = cls.env["product.product"].create(
            {
                "name": "Finished",
                "type": "consu",
                "is_storable": True,
                "route_ids": [Command.set(manufacture_route.ids)],
            }
        )
        cls.component = cls.env["product.product"].create(
            {"name": "Component", "type": "consu"}
        )
        cls.byproduct = cls.env["product.product"].create(
            {"name": "Byproduct", "type": "consu", "is_storable": True}
        )
        # BoM: 1 finished = 1 component (+) 2 byproduct
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.finished.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    Command.create({"product_id": cls.component.id, "product_qty": 1.0})
                ],
                "byproduct_ids": [
                    Command.create({"product_id": cls.byproduct.id, "product_qty": 2.0})
                ],
            }
        )

    def _confirm_mo(self, byproduct_auto_pick=True):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.finished
        mo_form.bom_id = self.bom
        mo_form.product_qty = 1.0
        mo = mo_form.save()
        mo.byproduct_auto_pick = byproduct_auto_pick
        mo.action_confirm()
        return mo

    def _recompute(self, mo):
        """Reproduce the recompute that 'Produce All' triggers."""
        mo.qty_producing = 1.0
        mo._set_qty_producing(False)

    def test_enabled_preserves_manual_quantity(self):
        mo = self._confirm_mo(byproduct_auto_pick=True)
        move = mo.move_byproduct_ids
        self.assertEqual(len(move), 1)
        move.quantity = 5.0
        # Editing the byproduct quantity auto-marks the line as picked.
        self.assertTrue(move.picked)
        self._recompute(mo)
        # The manual value survives the recompute.
        self.assertEqual(move.quantity, 5.0)

    def test_disabled_reverts_manual_quantity(self):
        mo = self._confirm_mo(byproduct_auto_pick=False)
        move = mo.move_byproduct_ids
        move.quantity = 5.0
        self.assertFalse(move.picked)
        self._recompute(mo)
        # Standard behavior: reset to the quantity to produce (2 per unit).
        self.assertEqual(move.quantity, 2.0)

    def test_tracked_byproduct_pick_on_line_edit(self):
        # For tracked byproducts the quantity field is read-only; the operator
        # enters quantities through the move lines (lot numbers) instead, which
        # the form sends as move_line_ids commands on the move.
        self.byproduct.write({"tracking": "lot"})
        mo = self._confirm_mo(byproduct_auto_pick=True)
        move = mo.move_byproduct_ids
        self.assertFalse(move.picked)
        line = move.move_line_ids[:1]
        if line:
            move.write(
                {
                    "move_line_ids": [
                        Command.update(
                            line.id, {"quantity": 5.0, "lot_name": "BP-LOT-1"}
                        )
                    ]
                }
            )
        else:
            move.write(
                {
                    "move_line_ids": [
                        Command.create(
                            {
                                "product_id": self.byproduct.id,
                                "quantity": 5.0,
                                "lot_name": "BP-LOT-1",
                                "location_id": move.location_id.id,
                                "location_dest_id": move.location_dest_id.id,
                            }
                        )
                    ]
                }
            )
        # Editing the lot line auto-marks the byproduct as picked.
        self.assertTrue(move.picked)
        self._recompute(mo)
        # The manually entered quantity survives the recompute.
        self.assertEqual(move.quantity, 5.0)

    def test_company_default_propagated(self):
        self.env.company.byproduct_auto_pick = True
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.finished
        mo_form.bom_id = self.bom
        mo_form.product_qty = 1.0
        mo = mo_form.save()
        # The computed field should pick up the company value.
        self.assertTrue(mo.byproduct_auto_pick)
        mo.action_confirm()
        move = mo.move_byproduct_ids
        move.quantity = 5.0
        self.assertTrue(move.picked)
        self._recompute(mo)
        self.assertEqual(move.quantity, 5.0)

    def test_company_default_off(self):
        self.env.company.byproduct_auto_pick = False
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.finished
        mo_form.bom_id = self.bom
        mo_form.product_qty = 1.0
        mo = mo_form.save()
        self.assertFalse(mo.byproduct_auto_pick)
