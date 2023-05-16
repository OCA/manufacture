# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase


class TestMrp(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.bom = cls.env.ref("mrp.mrp_bom_table_top")
        cls.bom.product_tmpl_id.categ_id.property_cost_method = "fifo"
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        for i, bom_line in enumerate(cls.bom.bom_line_ids):
            # Configure some component costs
            bom_line.product_id.standard_price = 10
            # Some initial stocks
            lot = cls.env["stock.lot"].create(
                {
                    "name": f"LOT_{i}",
                    "product_id": bom_line.product_id.id,
                    "company_id": cls.env.company.id,
                }
            )
            cls.env["stock.quant"].create(
                {
                    "product_id": bom_line.product_id.id,
                    "lot_id": lot.id,
                    "product_uom_id": bom_line.product_id.uom_id.id,
                    "quantity": 10.00,
                    "location_id": cls.location_stock.id,
                }
            )
        # Configure workcenter costs
        cls.bom_routing = cls.env.ref("mrp.mrp_routing_workcenter_0")
        cls.bom_routing.active = True
        cls.bom_routing.workcenter_id.costs_hour = 100
        # Create a MO
        with Form(cls.env["mrp.production"]) as mo_form:
            mo_form.product_id = cls.bom.product_id
            mo_form.bom_id = cls.bom
            mo_form.product_qty = 1
            cls.production = mo_form.save()
            cls.production.action_confirm()
            cls.production.action_generate_serial()

    def _mrp_production_done(self, production):
        for raw_move in production.move_raw_ids:
            raw_move.quantity_done = raw_move.product_uom_qty
        res = production.button_mark_done()
        self.assertEqual(production.state, "done", str(res))

    def test_workcenter_cost_effective(self):
        self.assertEqual(
            self.bom.product_tmpl_id.mrp_workcenter_cost,
            "effective",
            "The default value should be 'Effective' (odoo core behaviour)",
        )
        self.production.workorder_ids.duration = 30
        self._mrp_production_done(self.production)
        finished_move = self.production.move_finished_ids
        self.assertAlmostEqual(finished_move.price_unit, 70)

    def test_workcenter_cost_theoretical(self):
        self.bom.product_tmpl_id.mrp_workcenter_cost = "theoretical"
        self.production.workorder_ids.duration = 30
        self._mrp_production_done(self.production)
        self.assertEqual(self.production.workorder_ids.duration, 30)
        self.assertNotEqual(
            self.production.workorder_ids.duration,
            self.production.workorder_ids.duration_expected,
        )
        finished_move = self.production.move_finished_ids
        self.assertAlmostEqual(finished_move.price_unit, 120)
