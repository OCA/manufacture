# Copyright 2019 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestProductMrpInfo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pt_obj = cls.env["product.template"]
        cls.pp_obj = cls.env["product.product"]
        cls.mo_obj = cls.env["mrp.production"]
        cls.bom_obj = cls.env["mrp.bom"]
        cls.boml_obj = cls.env["mrp.bom.line"]

        cls.manufacture_route = cls.env.ref("mrp.route_warehouse0_manufacture")

        cls.attribute = cls.env["product.attribute"].create(
            {"name": "Test Attribute", "create_variant": "always"}
        )
        cls.value1 = cls.env["product.attribute.value"].create(
            {"name": "Value 1", "attribute_id": cls.attribute.id}
        )
        cls.value2 = cls.env["product.attribute.value"].create(
            {"name": "Value 2", "attribute_id": cls.attribute.id}
        )
        cls.product = cls.pt_obj.create(
            {
                "name": "Test Template",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attribute.id,
                            "value_ids": [(6, 0, [cls.value1.id, cls.value2.id])],
                        },
                    )
                ],
                "route_ids": [(6, 0, cls.manufacture_route.ids)],
            }
        )
        cls.variant_1 = cls.product.product_variant_ids[0]
        cls.variant_2 = cls.product.product_variant_ids[1]
        cls.bom = cls.bom_obj.create(
            {"product_tmpl_id": cls.product.id, "product_qty": 1.0}
        )
        # Create 3 MO's
        cls.mo_1 = cls.mo_obj.create(
            {
                "name": "MO ABC",
                "product_id": cls.variant_1.id,
                "product_uom_id": cls.variant_1.uom_id.id,
                "product_qty": 2,
                "bom_id": cls.bom.id,
            }
        )
        cls.mo_2 = cls.mo_obj.create(
            {
                "name": "MO XYZ",
                "product_id": cls.variant_1.id,
                "product_uom_id": cls.variant_1.uom_id.id,
                "product_qty": 3,
                "bom_id": cls.bom.id,
            }
        )
        cls.mo_3 = cls.mo_obj.create(
            {
                "name": "MO QWE",
                "product_id": cls.variant_2.id,
                "product_uom_id": cls.variant_2.uom_id.id,
                "product_qty": 6,
                "bom_id": cls.bom.id,
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
