# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestBomProduceDelay(TransactionCase):
    def setUp(self):
        super(TestBomProduceDelay, self).setUp()
        self.product_product_desk = self.env.ref("product.product_product_3")
        self.bom_desk = self.env.ref("mrp.mrp_bom_manufacture")

    def test_01_compute_produce_delay_in_hour(self):
        self.bom_desk._compute_produce_delay_in_hour()
        self.assertEqual(
            self.bom_desk.produce_delay_in_hour,
            self.product_product_desk.produce_delay_in_hour,
        )

    def test_02_inverse_produce_delay_in_hour(self):
        new_time = 42
        self.bom_desk.write({"produce_delay_in_hour": new_time})
        self.bom_desk._inverse_produce_delay_in_hour()
        self.assertEqual(
            self.product_product_desk.produce_delay_in_hour,
            new_time,
        )
