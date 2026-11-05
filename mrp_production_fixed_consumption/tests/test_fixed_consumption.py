# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, TransactionCase


class TestFixedConsumption(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.component = cls.env["product.product"].create(
            {"name": "Component", "type": "consu", "is_storable": True}
        )
        cls.finished = cls.env["product.product"].create(
            {"name": "Finished", "type": "consu", "is_storable": True}
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.component, cls.warehouse.lot_stock_id, 100
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.finished.product_tmpl_id.id,
                "product_qty": 1,
                "consumption": "strict",
                "fixed_consumption": True,
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.component.id, "product_qty": 2})
                ],
            }
        )

    def _create_production(self, qty):
        production = self.env["mrp.production"].create(
            {
                "product_id": self.finished.id,
                "product_qty": qty,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        production.action_assign()
        return production

    def _produce(self, production, qty):
        with Form(production) as form:
            form.qty_producing = qty

    def _close_without_backorder(self, production):
        action = production.button_mark_done()
        self.assertEqual(action["res_model"], "mrp.production.backorder")
        wizard = (
            self.env["mrp.production.backorder"]
            .with_context(**action["context"])
            .create({})
        )
        wizard.action_close_mo()

    def test_lower_quantity_keeps_planned_consumption(self):
        """Producing 8 of 10 consumes the components planned for 10."""
        production = self._create_production(10)
        move = production.move_raw_ids
        self.assertEqual(move.quantity, 20)
        self._produce(production, 8)
        self.assertEqual(move.quantity, 20)
        self.assertTrue(move.picked)
        # The strict consumption check compares with the planned quantity.
        self.assertFalse(production._get_consumption_issues())
        self._close_without_backorder(production)
        self.assertEqual(production.state, "done")
        self.assertEqual(production.qty_produced, 8)
        self.assertEqual(move.state, "done")
        self.assertEqual(move.quantity, 20)
        self.assertEqual(self.component.qty_available, 80)
        self.assertEqual(self.finished.qty_available, 8)

    def test_manual_consumption_is_kept(self):
        """A consumption registered by hand is not overwritten."""
        production = self._create_production(10)
        move = production.move_raw_ids
        move.with_context(force_manual_consumption=True).quantity = 18
        self.assertTrue(move.manual_consumption)
        self._produce(production, 8)
        self.assertEqual(move.quantity, 18)
        issues = production._get_consumption_issues()
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0][2:], (18, 20))

    def test_standard_flow_scales_consumption(self):
        """Without the option the consumption follows the produced quantity."""
        self.bom.fixed_consumption = False
        production = self._create_production(10)
        move = production.move_raw_ids
        self._produce(production, 8)
        self.assertEqual(move.quantity, 16)
        issues = production._get_consumption_issues()
        self.assertFalse(issues)
