from odoo.tests.common import TransactionCase


class TestProductTemplate(TransactionCase):
    def setUp(self):
        super().setUp()
        attribute_obj = self.env["product.attribute"]
        attribute_color = attribute_obj.create(
            {
                "name": "Color",
                "value_ids": [(0, 0, {"name": "Red"}), (0, 0, {"name": "Blue"})],
            }
        )
        attribute_size = attribute_obj.create(
            {
                "name": "Size",
                "value_ids": [(0, 0, {"name": "S"}), (0, 0, {"name": "L"})],
            }
        )
        self.product = self.env["product.template"].create(
            {
                "name": "Test Product",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute_color.id,
                            "value_ids": [(6, 0, attribute_color.value_ids.ids)],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute_size.id,
                            "value_ids": [(6, 0, attribute_size.value_ids.ids)],
                        },
                    ),
                ],
            }
        )

    def test_product_bom(self):
        action = self.product.action_duplicate_with_kit()
        self.assertIsNotNone(action["res_id"])
