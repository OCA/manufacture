# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests import Form, TransactionCase


class TestMrpFinishedBackorderProduct(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.component = cls.env["product.product"].create(
            {"name": "Test component", "is_storable": True}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test finished product", "is_storable": True}
        )
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": cls.component.id,
                "location_id": cls.env.ref("stock.warehouse0").lot_stock_id.id,
                "inventory_quantity": 10,
            }
        ).action_apply_inventory()
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "bom_line_ids": [
                    Command.create({"product_id": cls.component.id, "product_qty": 1})
                ],
            }
        )

    def _produce(self, production, qty):
        production.qty_producing = qty
        production.move_raw_ids.write({"quantity": qty, "picked": True})
        action = production.button_mark_done()
        if isinstance(action, dict) and action.get("res_model") == (
            "mrp.production.backorder"
        ):
            wizard = Form(
                self.env["mrp.production.backorder"].with_context(**action["context"])
            ).save()
            wizard.action_backorder()

    def test_the_finished_products_of_the_backorders_are_in_every_order(self):
        production = self.env["mrp.production"].create(
            {"product_id": self.product.id, "product_qty": 3, "bom_id": self.bom.id}
        )
        production.action_confirm()
        self._produce(production, 1)
        backorder = production.production_group_id.production_ids - production
        self.assertEqual(len(backorder), 1)
        self._produce(backorder, 1)
        orders = production.production_group_id.production_ids
        self.assertEqual(len(orders), 3)
        for order in orders:
            self.assertEqual(
                order.finished_move_from_backorder_ids,
                orders.move_finished_ids.move_line_ids.filtered(
                    lambda line: line.state == "done"
                ),
            )
        self.assertEqual(
            sum(production.finished_move_from_backorder_ids.mapped("quantity")), 2
        )
