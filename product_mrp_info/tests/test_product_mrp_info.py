# Copyright 2019 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestProductMrpInfo(TransactionCase):
    def setUp(self):
        super().setUp()
        self.pt_obj = self.env["product.template"]
        self.pp_obj = self.env["product.product"]
        self.mo_obj = self.env["mrp.production"]
        self.bom_obj = self.env["mrp.bom"]
        self.boml_obj = self.env["mrp.bom.line"]

        self.manufacture_route = self.env.ref("mrp.route_warehouse0_manufacture")

        self.attribute = self.env["product.attribute"].create(
            {"name": "Test Attribute", "create_variant": "always"}
        )
        self.value1 = self.env["product.attribute.value"].create(
            {"name": "Value 1", "attribute_id": self.attribute.id}
        )
        self.value2 = self.env["product.attribute.value"].create(
            {"name": "Value 2", "attribute_id": self.attribute.id}
        )
        self.product = self.pt_obj.create(
            {
                "name": "Test Template",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.attribute.id,
                            "value_ids": [(6, 0, [self.value1.id, self.value2.id])],
                        },
                    )
                ],
                "route_ids": [(6, 0, self.manufacture_route.ids)],
            }
        )
        self.variant_1 = self.product.product_variant_ids[0]
        self.variant_2 = self.product.product_variant_ids[1]
        self.bom = self.bom_obj.create(
            {"product_tmpl_id": self.product.id, "product_qty": 1.0}
        )
        # Create 3 MO's
        self.mo_1 = self.mo_obj.create(
            {
                "name": "MO ABC",
                "product_id": self.variant_1.id,
                "product_uom_id": self.variant_1.uom_id.id,
                "product_qty": 2,
                "bom_id": self.bom.id,
            }
        )
        self.mo_2 = self.mo_obj.create(
            {
                "name": "MO XYZ",
                "product_id": self.variant_1.id,
                "product_uom_id": self.variant_1.uom_id.id,
                "product_qty": 3,
                "bom_id": self.bom.id,
            }
        )
        self.mo_3 = self.mo_obj.create(
            {
                "name": "MO QWE",
                "product_id": self.variant_2.id,
                "product_uom_id": self.variant_2.uom_id.id,
                "product_qty": 6,
                "bom_id": self.bom.id,
            }
        )

    def test_01_mo_counters(self):
        self.assertEqual(len(self.product.product_variant_ids), 2)
        self.assertEqual(self.product.mo_count, 3)
        self.assertEqual(self.variant_1.mo_count, 2)
        self.assertEqual(self.variant_2.mo_count, 1)

    def test_02_actions(self):
        # template
        res = self.product.action_view_mrp_productions()
        count = self.mo_obj.search_count(res["domain"])
        self.assertEqual(count, 3)
        # variant
        res = self.variant_1.action_view_mrp_productions()
        count = self.mo_obj.search_count(res["domain"])
        self.assertEqual(count, 2)
