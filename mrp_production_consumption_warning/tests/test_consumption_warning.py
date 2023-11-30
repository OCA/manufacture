# Copyright 2023 Komit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase


class TestManufacturingOrderConsumptionWarningMessage(SavepointCase):

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.p_a = cls.env["product.product"].create({"name": "Product A"})
        cls.p_kit = cls.env["product.product"].create({"name": "Product Kit"})
        cls.p_1 = cls.env["product.product"].create({"name": "Product 1"})
        cls.p_2 = cls.env["product.product"].create({"name": "Product 2"})
        cls.p_3 = cls.env["product.product"].create({"name": "Product 3"})
        cls.p_4 = cls.env["product.product"].create({"name": "Product 4"})
        cls.p_5 = cls.env["product.product"].create({"name": "Product 5"})

        cls.bom_kit = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.p_kit.product_tmpl_id.id,
                "type": "phantom",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {"product_id": cls.p_1.id, "product_qty": 10},
                    ),
                    (
                        0,
                        0,
                        {"product_id": cls.p_2.id, "product_qty": 20},
                    ),
                ],
            }
        )
        cls.bom_a = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.p_a.product_tmpl_id.id,
                "type": "normal",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {"product_id": cls.p_kit.id, "product_qty": 2},
                    ),
                    (
                        0,
                        0,
                        {"product_id": cls.p_1.id, "product_qty": 5},
                    ),
                    (
                        0,
                        0,
                        {"product_id": cls.p_3.id, "product_qty": 10},
                    ),
                ],
            }
        )
        cls.mo_a = cls.env["mrp.production"].create(
            {
                "product_id": cls.p_a.id,
                "product_uom_id": cls.p_a.uom_id.id,
                "bom_id": cls.bom_a.id,
                "consumption": "warning",
            }
        )
        cls.mo_a._onchange_move_raw()

    def test_consumption_warning_message_when_create(self):
        self.assertEqual(self.mo_a.consumption_warning_msg, "")

    def test_consumption_warning_message_when_edit(self):
        # Add new line into BoM of product A
        self.env["mrp.bom.line"].create(
            {"bom_id": self.bom_a.id, "product_id": self.p_5.id}
        )
        # Update quantity of a line in BoM of product A
        self.env["mrp.bom.line"].search(
            [("bom_id", "=", self.bom_a.id), ("product_id", "=", self.p_1.id)]
        ).product_qty = 10
        # Add new line into MO of product A
        self.env["stock.move"].create(
            {
                "name": self.mo_a.name,
                "location_id": self.mo_a.location_src_id.id,
                "location_dest_id": self.mo_a.location_src_id.id,
                "raw_material_production_id": self.mo_a.id,
                "product_id": self.p_4.id,
                "product_uom_qty": 1,
                "product_uom": self.p_4.uom_id.id,
            }
        )
        # Remove a line in MO of product A
        self.env["stock.move"].search(
            [
                ("raw_material_production_id", "=", self.mo_a.id),
                ("product_id", "=", self.p_3.id),
            ]
        ).unlink()
        self.assertEqual(
            self.mo_a.consumption_warning_msg,
            "There are discrepancies between your Manufacturing Order and the "
            "BoM associated with the Finished products:\n"
            "- The MO does not use the product(s) Product 3, Product 5\n"
            "- The MO line quantity for Product Product 1 is 25.0 while the quantity "
            "of 30.0 (30.0 x 1.0) is expected from the BoM line\n"
            "- The components Product 4 is/are not present on the BoM\n",
        )
