# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestMrpProductionInjectOperation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.tz = "UTC"
        cls.product_produce = cls.env["product.product"].create(
            {
                "name": "Product to Produce",
                "type": "product",
            }
        )
        cls.product_comp_1 = cls.env["product.product"].create(
            {
                "name": "Product Component 1",
                "type": "product",
            }
        )
        cls.product_comp_2 = cls.env["product.product"].create(
            {
                "name": "Product Component 2",
                "type": "product",
            }
        )
        bom_form = Form(cls.env["mrp.bom"])
        bom_form.product_id = cls.product_produce
        bom_form.product_tmpl_id = cls.product_produce.product_tmpl_id
        bom_form.type = "normal"
        with bom_form.bom_line_ids.new() as bom_line:
            bom_line.product_id = cls.product_comp_1
        with bom_form.bom_line_ids.new() as bom_line:
            bom_line.product_id = cls.product_comp_2
        cls.bom = bom_form.save()

    def test_mrp_production_generator(self):
        wiz_form = Form(self.env["mrp.production.generator.date.interval.wizard"])
        wiz_form.product_id = self.product_produce
        self.assertEqual(wiz_form.bom_id, self.bom)
        wiz_form.period_date_start = fields.Date.to_date("2025-05-15")
        wiz_form.period_date_end = fields.Date.to_date("2025-05-22")
        wiz_form.hour_start = 17.00
        wiz = wiz_form.save()
        action = wiz.action_create_production()
        productions = self.env["mrp.production"].search(action["domain"])
        self.assertEqual(len(productions), 8)
        self.assertTrue(
            all(
                [
                    production.product_id == self.product_produce
                    for production in productions
                ]
            )
        )
        self.assertTrue(
            all([production.bom_id == self.bom for production in productions])
        )
        self.assertTrue(
            all([production.date_start.hour == 17 for production in productions])
        )
        self.assertTrue(
            all(
                [
                    self.product_comp_1 in production.move_raw_ids.product_id
                    for production in productions
                ]
            )
        )
        self.assertTrue(
            all(
                [
                    self.product_comp_2 in production.move_raw_ids.product_id
                    for production in productions
                ]
            )
        )
