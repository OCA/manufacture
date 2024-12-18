# Copyright 2024 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import Form

from odoo.addons.base.tests.common import BaseCommon


class TestMRPMassProductionOrder(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_delivery_01 = cls.env["product.product"].create(
            {"name": "Test product 1"}
        )
        cls.product_delivery_02 = cls.env["product.product"].create(
            {"name": "Test product 2"}
        )
        cls.component_1 = cls.env["product.product"].create({"name": "Test comp 1"})
        cls.component_2 = cls.env["product.product"].create({"name": "Test comp 2"})
        cls.tag = cls.env["mrp.tag"].create({"name": "With_bom"})
        cls.tag2 = cls.env["mrp.tag"].create({"name": "Without_bom"})
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_delivery_01.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.component_1.id,
                            "product_qty": 2,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.component_2.id,
                            "product_qty": 2,
                        }
                    ),
                ],
            }
        )

        wizard_with_bom = Form(
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
        wizard_with_bom.save().action_create()
        cls.mrp1, cls.mrp2 = cls.env["mrp.production"].search(
            [
                (
                    "product_id",
                    "in",
                    [cls.product_delivery_01.id, cls.product_delivery_02.id],
                ),
                (
                    "tag_ids",
                    "in",
                    [cls.tag.id],
                ),
            ]
        )

        # Without bom
        wizard_without_bom = Form(
            cls.env["mrp.mass.production.order.wizard"].with_context(
                default_mrp_production_order_entries=[
                    Command.create(
                        {
                            "product_id": cls.product_delivery_02.id,
                            "product_qty": 2,
                            "product_consumed_id": cls.product_delivery_01.id,
                            "quantity": 2,
                        }
                    )
                ],
                default_tag_ids=[cls.tag2.id],
            ),
            "mrp_mass_production_order.wizard_mass_mrp_production_order",
        )
        wizard_without_bom.save().action_create()
        cls.mrp3 = cls.env["mrp.production"].search(
            [
                (
                    "product_id",
                    "in",
                    [cls.product_delivery_02.id],
                ),
                (
                    "tag_ids",
                    "in",
                    [cls.tag2.id],
                ),
            ]
        )

    def test_wizard_mrp_without_bom(self):
        self.assertEqual(self.mrp3.product_uom_id, self.product_delivery_01.uom_id)
        self.assertEqual(self.mrp3.product_qty, 2)
        picking_type = self.env["stock.picking.type"].search(
            [
                ("code", "=", "mrp_operation"),
            ],
            limit=1,
        )
        self.assertEqual(self.mrp3.state, "done")
        self.assertEqual(self.mrp3.tag_ids, self.tag2)
        self.assertEqual(self.mrp3.picking_type_id, picking_type)
        self.assertEqual(
            self.mrp3.location_src_id, picking_type.default_location_src_id
        )
        self.assertEqual(
            self.mrp3.location_dest_id, picking_type.default_location_dest_id
        )

    def test_wizard_mrp_with_bom(self):
        self.assertEqual(self.mrp1.bom_id, self.bom)
        self.assertEqual(self.mrp1.product_uom_id, self.product_delivery_01.uom_id)
        self.assertEqual(len(self.mrp2.bom_id), 0)
        self.assertEqual(self.mrp2.product_qty, 1)
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
