# -*- coding: utf-8 -*-
# © 2015 AvanzOSC
# © 2015 Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from datetime import datetime


class TestProcurement(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(TestProcurement, self).setUp(*args, **kwargs)

        self.product = self.env.ref("product.product_product_4b")
        self.location = self.env.ref("stock.stock_location_stock")

        criteria = [
            ("location_id", "=", self.location.id),
            ("action", "=", "manufacture"),
        ]

        self.rule = self.env["procurement.rule"].search(
            criteria)[0]

        self.proc_data = {
            "name": "Test Procurement",
            "product_id": self.product.id,
            "location_id": self.location.id,
            "product_qty": 1.0,
            "product_uom": self.product.uom_id.id,
            "date_planned": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "rule_id": self.rule.id,
        }

        return result

    def test_1(self):
        proc = self.env["procurement.order"].create(self.proc_data)

        proc.run()
        self.assertEqual(
            proc.state,
            "running")

        # procurement should generate MO
        self.assertTrue(proc.production_id)

        # MO should in draft state
        self.assertEqual(
            proc.production_id.state,
            "draft")
