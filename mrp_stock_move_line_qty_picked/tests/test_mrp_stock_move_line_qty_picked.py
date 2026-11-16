# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import Command
from odoo.tests import Form, tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("-at_install", "post_install")
class TestMrpStockMoveLineQtyPicked(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loc = cls.env.ref("stock.stock_location_stock")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Finished Product",
                "is_storable": True,
            }
        )
        cls.component = cls.env["product.product"].create(
            {
                "name": "Component",
                "is_storable": True,
            }
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_qty": 1,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.component.id,
                            "product_qty": 1,
                        }
                    )
                ],
            }
        )
        cls.env["stock.quant"]._update_available_quantity(cls.component, cls.loc, 10)

    def _create_mo(self, qty=10):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.product
        mo_form.bom_id = self.bom
        mo_form.product_qty = qty
        mo = mo_form.save()
        mo.action_confirm()
        mo.action_assign()
        return mo

    def _set_qty_producing(self, mo, qty):
        with Form(mo) as mo_form:
            mo_form.qty_producing = qty

    def test_lower_qty_producing(self):
        mo = self._create_mo()
        move = mo.move_raw_ids
        self._set_qty_producing(mo, 5)
        self.assertRecordValues(move.move_line_ids, [{"quantity": 5, "qty_picked": 5}])
        self._set_qty_producing(mo, 3)
        self.assertRecordValues(move.move_line_ids, [{"quantity": 3, "qty_picked": 3}])
        self.assertEqual(move._get_picked_quantity(), 3)
        mo.with_context(skip_backorder=True, mo_ids_to_backorder=[]).button_mark_done()
        self.assertEqual(mo.state, "done")
        self.assertRecordValues(move, [{"state": "done", "quantity": 3}])

    def test_lower_qty_producing_direct(self):
        mo = self._create_mo()
        move = mo.move_raw_ids
        for qty in (5, 3):
            mo.qty_producing = qty
            mo._set_qty_producing(False)
        self.assertRecordValues(move.move_line_ids, [{"quantity": 3, "qty_picked": 3}])

    def test_partial_pick_is_kept(self):
        mo = self._create_mo()
        move = mo.move_raw_ids
        self._set_qty_producing(mo, 5)
        line = move.move_line_ids
        # The picked quantity was set on the line on purpose
        line.qty_picked = 4
        self._set_qty_producing(mo, 3)
        self.assertRecordValues(line, [{"quantity": 3, "qty_picked": 4}])

    def test_manual_component_quantity_keeps_picked(self):
        mo = self._create_mo()
        move = mo.move_raw_ids
        self._set_qty_producing(mo, 5)
        # Raising grows reserved line, lowering reduces it
        # In both cases the picked quantity is kept
        for qty in (7, 4):
            with Form(mo) as mo_form:
                with mo_form.move_raw_ids.edit(0) as move_form:
                    move_form.quantity = qty
            self.assertRecordValues(
                move.move_line_ids, [{"quantity": qty, "qty_picked": 5}]
            )
