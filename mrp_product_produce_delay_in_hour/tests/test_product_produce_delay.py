# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProductProduceDelay(TransactionCase):
    def setUp(self):
        super(TestProductProduceDelay, self).setUp()
        self.product_acoustic_bloc = self.env.ref(
            "product.product_product_25_product_template"
        )

    def test_01_produce_delay_hour(self):
        self.product_acoustic_bloc.write({"produce_delay_in_hour": 12})
        self.product_acoustic_bloc._onchange_produce_delay_in_hour()
        self.assertEqual(self.product_acoustic_bloc.produce_delay, 0.5)
