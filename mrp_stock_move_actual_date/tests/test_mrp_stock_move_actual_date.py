# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from datetime import date

from freezegun import freeze_time

from odoo import Command
from odoo.tests import Form, common


class TestMrpStockActualDate(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["product.category"].create(
            {"name": "Test Category", "property_valuation": "real_time"}
        )
        cls.product_finished = cls.env["product.product"].create(
            {
                "name": "Finished Product",
                "type": "product",
                "categ_id": cls.category.id,
                "standard_price": 100.0,
            }
        )
        cls.product_component = cls.env["product.product"].create(
            {
                "name": "Component Product",
                "type": "product",
                "categ_id": cls.category.id,
                "standard_price": 100.0,
            }
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_finished.product_tmpl_id.id,
                "product_qty": 1.0,
                "bom_line_ids": [
                    Command.create(
                        {"product_id": cls.product_component.id, "product_qty": 1.0}
                    ),
                ],
            }
        )

    def create_mo(self, actual_date=False):
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product_finished.id,
                "product_qty": 1.0,
                "bom_id": self.bom.id,
                "actual_date": actual_date,
            }
        )
        mo.action_confirm()
        mark_done_action = mo.button_mark_done()
        immediate_production_wizard = Form(
            self.env["mrp.immediate.production"].with_context(
                **mark_done_action["context"]
            )
        ).save()
        immediate_production_wizard.process()
        return mo

    def create_scrap(self, mo, actual_date=False):
        scrap = self.env["stock.scrap"].create(
            {
                "product_id": self.product_finished.id,
                "scrap_qty": 1.0,
                "production_id": mo.id,
                "actual_date": actual_date,
            }
        )
        scrap.action_validate()
        return scrap

    def create_unbuild_order(self, mo, actual_date=False):
        unbuild_order = self.env["mrp.unbuild"].create(
            {
                "product_id": self.product_finished.id,
                "bom_id": self.bom.id,
                "product_qty": 1.0,
                "mo_id": mo.id,
                "actual_date": actual_date,
            }
        )
        unbuild_order.action_unbuild()
        return unbuild_order

    def test_mo_actual_dates(self):
        mo = self.create_mo(date(2025, 3, 10))
        self.assertEqual(mo.move_raw_ids.actual_date, date(2025, 3, 10))
        self.assertEqual(mo.move_raw_ids.account_move_ids.date, date(2025, 3, 10))
        self.assertEqual(mo.move_finished_ids.actual_date, date(2025, 3, 10))
        self.assertEqual(mo.move_finished_ids.account_move_ids.date, date(2025, 3, 10))
        mo.actual_date = date(2025, 2, 1)
        self.assertEqual(mo.move_raw_ids.actual_date, date(2025, 2, 1))
        self.assertEqual(mo.move_raw_ids.account_move_ids.date, date(2025, 2, 1))
        self.assertEqual(mo.move_finished_ids.actual_date, date(2025, 2, 1))
        self.assertEqual(mo.move_finished_ids.account_move_ids.date, date(2025, 2, 1))
        scrap = self.create_scrap(mo, date(2025, 3, 10))
        self.assertEqual(scrap.move_id.actual_date, date(2025, 3, 10))
        self.assertEqual(scrap.move_id.account_move_ids.date, date(2025, 3, 10))
        scrap.actual_date = date(2025, 2, 1)
        self.assertEqual(scrap.move_id.actual_date, date(2025, 2, 1))
        self.assertEqual(scrap.move_id.account_move_ids.date, date(2025, 2, 1))
        unbuild_order = self.create_unbuild_order(mo, date(2025, 3, 10))
        self.assertEqual(
            unbuild_order.produce_line_ids[0].actual_date, date(2025, 3, 10)
        )
        self.assertEqual(
            unbuild_order.produce_line_ids[0].account_move_ids.date, date(2025, 3, 10)
        )
        unbuild_order.actual_date = date(2025, 2, 1)
        self.assertEqual(
            unbuild_order.produce_line_ids[0].actual_date, date(2025, 2, 1)
        )
        self.assertEqual(
            unbuild_order.produce_line_ids[0].account_move_ids.date, date(2025, 2, 1)
        )

    @freeze_time("2025-03-6 23:00:00")
    def test_mo_without_actual_date(self):
        self.env.user.tz = "Asia/Tokyo"
        mo = self.create_mo()
        self.assertEqual(mo.move_raw_ids.actual_date, date(2025, 3, 7))
        self.assertEqual(mo.move_raw_ids.account_move_ids.date, date(2025, 3, 7))
        self.assertEqual(mo.move_finished_ids.actual_date, date(2025, 3, 7))
        self.assertEqual(mo.move_finished_ids.account_move_ids.date, date(2025, 3, 7))
        scrap = self.create_scrap(mo)
        self.assertEqual(scrap.move_id.actual_date, date(2025, 3, 7))
        self.assertEqual(scrap.move_id.account_move_ids.date, date(2025, 3, 7))
        unbuild_order = self.create_unbuild_order(mo)
        self.assertEqual(
            unbuild_order.produce_line_ids[0].actual_date, date(2025, 3, 7)
        )
        self.assertEqual(
            unbuild_order.produce_line_ids[0].account_move_ids.date, date(2025, 3, 7)
        )
