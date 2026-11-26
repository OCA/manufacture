# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import Command
from odoo.tests import Form, tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("-at_install", "post_install")
class TestMrpQtyPickedNewLines(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Finished Product", "is_storable": True}
        )
        # No stock: raising quantity producing creates new lines instead of
        # increasing reserved ones
        cls.component = cls.env["product.product"].create(
            {"name": "Component", "is_storable": True}
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_qty": 1,
                "bom_line_ids": [
                    Command.create({"product_id": cls.component.id, "product_qty": 1})
                ],
            }
        )

    def test_new_line_sent_without_picked(self):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.product
        mo_form.bom_id = self.bom
        mo_form.product_qty = 10
        mo = mo_form.save()
        mo.action_confirm()
        with Form(mo) as mo_form:
            mo_form.qty_producing = 1
        move = mo.move_raw_ids
        self.assertRecordValues(
            move.move_line_ids, [{"quantity": 1, "picked": True, "qty_picked": 1}]
        )
        # Once move details were opened, the form also loads the move lines
        spec = Form(mo)._view["fields_spec"]
        spec["move_raw_ids"]["fields"]["move_line_ids"] = {
            "fields": dict.fromkeys(
                [
                    "quantity",
                    "qty_picked",
                    "product_id",
                    "product_uom_id",
                    "location_id",
                    "location_dest_id",
                ],
                {},
            )
        }
        res = mo.onchange({"qty_producing": 2}, ["qty_producing"], spec)
        move_vals = res["value"]["move_raw_ids"][0][2]
        mo.write(
            {
                "qty_producing": 2,
                "move_raw_ids": [
                    Command.update(
                        move.id,
                        {
                            "quantity": move_vals["quantity"],
                            "move_line_ids": [
                                Command.create(command[2])
                                for command in move_vals["move_line_ids"]
                                if command[0] == Command.CREATE
                            ],
                        },
                    )
                ],
            }
        )
        self.assertRecordValues(
            move.move_line_ids.sorted("id"),
            [
                {"quantity": 1, "picked": True, "qty_picked": 1},
                {"quantity": 1, "picked": True, "qty_picked": 1},
            ],
        )
        mo.with_context(skip_backorder=True, mo_ids_to_backorder=[]).button_mark_done()
        self.assertRecordValues(move, [{"state": "done", "quantity": 2}])
