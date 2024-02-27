# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBomProductVariant(TransactionCase):
    def setUp(self):
        super(TestBomProductVariant, self).setUp()
        self.product_template_desk = self.env.ref(
            "product.product_product_3_product_template"
        )
        self.product_template_bolt = self.env.ref(
            "mrp.product_product_computer_desk_bolt_product_template"
        )
        self.product_product_desk = self.env.ref("product.product_product_3")
        self.bom_desk = self.env.ref("mrp.mrp_bom_manufacture")

    def test_01_add_variant_in_bom(self):
        self.bom_desk.write({"product_id": self.product_product_desk.id})
        self.bom_desk._onchange_product_id()
        self.assertEqual(
            self.bom_desk.product_tmpl_id,
            self.bom_desk.product_id.product_tmpl_id,
        )

    def test_02_constrains(self):
        with self.assertRaises(ValidationError):
            self.bom_desk.product_id = self.product_product_desk
            self.bom_desk.product_tmpl_id = self.product_template_bolt.id
