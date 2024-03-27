# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
from odoo.addons.mrp.tests.common import TestMrpCommon


class MrpBomFind(TestMrpCommon):
    def test_bom_find(self):
        product = self.bom_1.product_id
        bom = self.env["mrp.bom"]._bom_find(product=product)
        self.assertEqual(bom, self.bom_1)

        bom = (
            self.env["mrp.bom"]
            .with_context(ignore_bom_find=True)
            ._bom_find(product=product)
        )
        self.assertFalse(bom)
