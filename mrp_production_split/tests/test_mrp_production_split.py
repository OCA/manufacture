# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.exceptions import UserError

from .common import CommonCase


class TestMrpProductionSplit(CommonCase):
    def test_mrp_production_split_draft(self):
        with self.assertRaisesRegex(UserError, r"Cannot split.*"):
            self._mrp_production_split(self.production)

    def test_mrp_production_split_done(self):
        self.production.action_confirm()
        self.production.action_generate_serial()
        self._mrp_production_set_quantity_done(self.production)
        self.production.button_mark_done()
        with self.assertRaisesRegex(UserError, r"Cannot split.*"):
            self._mrp_production_split(self.production)

    def test_mrp_production_split_cancel(self):
        self.production.action_cancel()
        with self.assertRaisesRegex(UserError, r"Cannot split.*"):
            self._mrp_production_split(self.production)

    def test_mrp_production_split_lot_simple(self):
        self.production.action_confirm()
        self.production.action_generate_serial()
        mos = self._mrp_production_split(self.production, split_qty=2.0)
        self.assertRecordValues(mos, [dict(product_qty=3.0), dict(product_qty=2.0)])

    def test_mrp_production_split_lot_simple_copy_date_planned(self):
        dt_start = datetime.now() + timedelta(days=5)
        dt_finished = dt_start + timedelta(hours=1)
        self.production.date_planned_start = dt_start
        self.production.date_planned_finished = dt_finished
        self.production.action_confirm()
        self.production.action_generate_serial()
        mos = self._mrp_production_split(self.production, split_qty=2.0)
        self.assertRecordValues(
            mos,
            [
                dict(
                    product_qty=3.0,
                    date_planned_start=dt_start,
                    date_planned_finished=dt_finished,
                ),
                dict(
                    product_qty=2.0,
                    date_planned_start=dt_start,
                    date_planned_finished=dt_finished,
                ),
            ],
        )

    def test_mrp_production_split_lot_simple_zero_qty(self):
        self.production.action_confirm()
        self.production.action_generate_serial()
        with self.assertRaisesRegex(UserError, r"Nothing to split.*"):
            self._mrp_production_split(self.production, split_qty=0.0)

    def test_mrp_production_split_lot_simple_with_qty_producing_exceeded(self):
        self.production.action_confirm()
        self.production.action_generate_serial()
        self.production.qty_producing = 3.0
        with self.assertRaisesRegex(UserError, r"You can't split.*"):
            self._mrp_production_split(self.production, split_qty=4.0)

    def test_mrp_production_split_lot_equal(self):
        self.production.action_confirm()
        self.production.action_generate_serial()
        mos = self._mrp_production_split(
            self.production,
            split_mode="equal",
            split_qty=4.0,
            split_equal_qty=2.0,
        )
        self.assertRecordValues(
            mos,
            [
                dict(product_qty=1.0),
                dict(product_qty=2.0),
                dict(product_qty=2.0),
            ],
        )

    def test_mrp_production_split_lot_custom(self):
        self.production.action_confirm()
        self.production.action_generate_serial()
        mos = self._mrp_production_split(
            self.production,
            split_mode="custom",
            custom_quantities="1 2 1 1",
        )
        self.assertRecordValues(
            mos,
            [
                dict(product_qty=1.0),
                dict(product_qty=2.0),
                dict(product_qty=1.0),
                dict(product_qty=1.0),
            ],
        )

    def test_mrp_production_split_lot_custom_incomplete(self):
        self.production.action_confirm()
        self.production.action_generate_serial()
        mos = self._mrp_production_split(
            self.production,
            split_mode="custom",
            custom_quantities="1 2",
        )
        self.assertRecordValues(
            mos,
            [
                dict(product_qty=2.0),
                dict(product_qty=1.0),
                dict(product_qty=2.0),
            ],
        )

    def test_mrp_production_split_lot_custom_float(self):
        self.production.action_confirm()
        self.production.action_generate_serial()
        mos = self._mrp_production_split(
            self.production,
            split_mode="custom",
            custom_quantities="1.0 2.0 1.0 1.0",
        )
        self.assertRecordValues(
            mos,
            [
                dict(product_qty=1.0),
                dict(product_qty=2.0),
                dict(product_qty=1.0),
                dict(product_qty=1.0),
            ],
        )

    def test_mrp_production_split_lot_custom_float_locale(self):
        lang = self.env["res.lang"]._lang_get(self.env.user.lang)
        lang.decimal_point = ","
        lang.thousands_sep = ""
        self.production.action_confirm()
        self.production.action_generate_serial()
        mos = self._mrp_production_split(
            self.production,
            split_mode="custom",
            custom_quantities="1,0 2,0 1,0 1,0",
        )
        self.assertRecordValues(
            mos,
            [
                dict(product_qty=1.0),
                dict(product_qty=2.0),
                dict(product_qty=1.0),
                dict(product_qty=1.0),
            ],
        )

    def test_mrp_production_split_serial(self):
        self.product.tracking = "serial"
        self.production.action_confirm()
        mos = self._mrp_production_split(self.production)
        self.assertRecordValues(
            mos,
            [
                dict(product_qty=1.0),
                dict(product_qty=1.0),
                dict(product_qty=1.0),
                dict(product_qty=1.0),
                dict(product_qty=1.0),
            ],
        )
