# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProductProduct(TransactionCase):
    def setUp(self):
        super(TestProductProduct, self).setUp()
        self.mrp_bom = self.env["mrp.bom"]
        self.product_product_screw = self.env.ref(
            "mrp.product_product_computer_desk_screw"
        )

    def test_01_change_from_component_to_intermediate(self):
        self.assertEqual(
            self.product_product_screw.is_component,
            True,
        )
        self.assertEqual(
            self.product_product_screw.is_intermediate,
            False,
        )
        self.mrp_bom.create(
            {
                "product_id": self.product_product_screw.id,
                "product_tmpl_id": self.product_product_screw.product_tmpl_id.id,
            }
        )
        self.product_product_screw._compute_is_component_intermediate()
        self.assertEqual(
            self.product_product_screw.is_component,
            False,
        )
        self.assertEqual(
            self.product_product_screw.is_intermediate,
            True,
        )
