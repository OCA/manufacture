# Copyright 2024 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import Form, TransactionCase


class TestMRPMassProductionOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_delivery_01 = cls.env.ref("product.product_delivery_01")
        cls.product_delivery_02 = cls.env.ref("product.product_delivery_02")
        cls.tag = cls.env["mrp.tag"].create({"name": "Test"})
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_delivery_01.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.env.ref("product.product_order_01").id,
                            "product_qty": 2,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.env.ref("product.product_product_3").id,
                            "product_qty": 2,
                        }
                    ),
                ],
            }
        )

        wizard_form = Form(
            cls.env["mrp.mass.production.order.wizard"].with_context(
                default_mrp_production_order_entries=[
                    Command.create(
                        {"product_id": cls.product_delivery_01.id, "product_qty": 2}
                    ),
                    Command.create({"product_id": cls.product_delivery_02.id}),
                ],
                default_tag_ids=[cls.tag.id],
            ),
            "mrp_mass_production_order.wizard_mass_mrp_production_order",
        )
        wizard_form.save().action_create()
        cls.mrp1, cls.mrp2 = cls.env["mrp.production"].search(
            [
                (
                    "product_id",
                    "in",
                    [cls.product_delivery_01.id, cls.product_delivery_02.id],
                )
            ]
        )

    def test_wizard_mrp_mass_entries(self):
        self.assertEqual(self.mrp1.bom_id, self.bom)
        self.assertEqual(self.mrp1.product_uom_id, self.product_delivery_01.uom_id)
        self.assertEqual(len(self.mrp2.bom_id), 0)
        self.assertEqual(self.mrp2.product_qty, 1)

    def test_wizard_mrp(self):
        picking_type = self.env["stock.picking.type"].search(
            [
                ("code", "=", "mrp_operation"),
            ],
            limit=1,
        )
        self.assertEqual(self.mrp1.state and self.mrp2.state, "done")
        self.assertEqual(self.mrp1.tag_ids and self.mrp2.tag_ids, self.tag)
        self.assertEqual(self.mrp1.picking_type_id, picking_type)
        self.assertEqual(
            self.mrp1.location_src_id, picking_type.default_location_src_id
        )
        self.assertEqual(
            self.mrp1.location_dest_id, picking_type.default_location_dest_id
        )
