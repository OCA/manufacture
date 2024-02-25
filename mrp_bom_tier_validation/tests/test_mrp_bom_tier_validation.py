# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common


class TestMrpBom(common.TransactionCase):
    def setUp(self):
        super(TestMrpBom, self).setUp()

        # common models
        self.mrp_bom = self.env["mrp.bom"]
        self.tier_definition = self.env["tier.definition"]

    def test_get_tier_validation_model_names(self):
        self.assertIn(
            "mrp.bom", self.tier_definition._get_tier_validation_model_names()
        )
