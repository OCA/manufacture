# Copyright (C) 2017 Akretion (http://www.akretion.com). All Rights Reserved
# @author Florian DA COSTA <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestProgressButton(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.production_model = self.env["mrp.production"]
        self.bom_model = self.env["mrp.bom"]
        self.manufacture_route = self.env.ref("mrp.route_warehouse0_manufacture")
        self.uom_unit = self.env.ref("uom.product_uom_unit")

        self.product_manuf = self.env["product.product"].create(
            {
                "name": "Manuf",
                "type": "consu",
                "uom_id": self.uom_unit.id,
                "route_ids": [(4, self.manufacture_route.id)],
            }
        )
        self.product_raw_material = self.env["product.product"].create(
            {
                "name": "Raw Material",
                "type": "consu",
                "uom_id": self.uom_unit.id,
            }
        )

        self.bom = self.env["mrp.bom"].create(
            {
                "product_id": self.product_manuf.id,
                "product_tmpl_id": self.product_manuf.product_tmpl_id.id,
                "bom_line_ids": (
                    [
                        (
                            0,
                            0,
                            {
                                "product_id": self.product_raw_material.id,
                                "product_qty": 1,
                                "product_uom_id": self.uom_unit.id,
                            },
                        ),
                    ]
                ),
            }
        )

    def test_01_manufacture_with_forecast_stock(self):
        """
        Test Manufacture mto with stock based on forecast quantity
        and no link between sub assemblies MO's and Main MO raw material
        """
        production = self._create_production()
        production.action_confirm()
        date_start = production.date_start
        move_date = production.move_raw_ids.date
        production.action_start()
        self.assertEqual(production.state, "progress")
        self.assertEqual(
            production.date_started.replace(microsecond=0),
            fields.Datetime.now().replace(microsecond=0),
        )
        self.assertEqual(production.date_start, date_start)
        self.assertEqual(production.move_raw_ids.date, move_date)
        production.action_unstart()
        self.assertEqual(production.state, "confirmed")
        self.assertEqual(production.qty_producing, 0)
        self.assertFalse(production.date_started)

    def _create_production(self):
        return self.production_model.create(
            {
                "product_id": self.product_manuf.id,
                "product_qty": 1,
                "product_uom_id": self.uom_unit.id,
                "bom_id": self.bom.id,
            }
        )

    def _create_production_with_workorder(self, operations=1):
        workcenter = self.env["mrp.workcenter"].create({"name": "Workcenter"})
        self.bom.operation_ids = [
            (0, 0, {"name": f"Operation {i}", "workcenter_id": workcenter.id})
            for i in range(operations)
        ]
        return self._create_production()

    def test_02_start_planned_production_keeps_schedule(self):
        production = self._create_production_with_workorder()
        production.action_confirm()
        production.button_plan()
        self.assertTrue(production.is_planned)
        wo_date_start = production.workorder_ids.date_start
        production.action_start()
        self.assertEqual(production.state, "progress")
        self.assertTrue(production.is_planned)
        self.assertEqual(production.workorder_ids.date_start, wo_date_start)

    def test_03_unstart_with_done_workorder(self):
        production = self._create_production_with_workorder(operations=2)
        production.action_confirm()
        production.action_start()
        production.workorder_ids[0].state = "done"
        self.assertEqual(production.state, "progress")
        with self.assertRaises(UserError):
            production.action_unstart()

    def test_04_unstart_with_picked_component(self):
        production = self._create_production()
        production.action_confirm()
        production.action_start()
        production.move_raw_ids.picked = True
        with self.assertRaises(UserError):
            production.action_unstart()
        self.assertEqual(production.state, "progress")

    def test_05_unstart_not_in_progress(self):
        production = self._create_production()
        production.action_confirm()
        with self.assertRaises(UserError):
            production.action_unstart()

    def test_06_workorder_start_sets_date_started(self):
        production = self._create_production_with_workorder()
        production.action_confirm()
        production.workorder_ids.button_start()
        self.assertEqual(production.state, "progress")
        self.assertTrue(production.date_started)

    def test_07_qty_producing_sets_date_started(self):
        self.bom.product_qty = 2
        production = self._create_production()
        production.product_qty = 2
        production.action_confirm()
        production.qty_producing = 1
        self.assertEqual(production.state, "progress")
        self.assertTrue(production.date_started)

    def test_08_picked_component_sets_date_started(self):
        production = self._create_production()
        production.action_confirm()
        production.move_raw_ids.picked = True
        self.assertEqual(production.state, "progress")
        self.assertTrue(production.date_started)

    def test_09_date_started_kept_on_done_and_cancel(self):
        production = self._create_production()
        production.action_confirm()
        production.action_start()
        date_started = production.date_started
        production.action_cancel()
        self.assertEqual(production.state, "cancel")
        self.assertEqual(production.date_started, date_started)
        production = self._create_production()
        production.action_confirm()
        production.action_start()
        date_started = production.date_started
        production.qty_producing = 1
        production.move_raw_ids.picked = True
        production.button_mark_done()
        self.assertEqual(production.state, "done")
        self.assertEqual(production.date_started, date_started)
