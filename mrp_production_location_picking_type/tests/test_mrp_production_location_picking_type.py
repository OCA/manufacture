# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMrpProductionLocationPickingType(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product_model = self.env["product.product"]
        self.bom_model = self.env["mrp.bom"]
        self.location_model = self.env["stock.location"]
        self.picking_type_model = self.env["stock.picking.type"]
        self.production_model = self.env["mrp.production"]
        self.warehouse = self.env.ref("stock.warehouse0")
        self.stock_location = self.warehouse.lot_stock_id
        self.custom_production_location = self.location_model.create(
            {
                "name": "Custom Production Location",
                "usage": "production",
                "location_id": self.warehouse.view_location_id.id,
            }
        )
        self.custom_picking_type = self.picking_type_model.create(
            {
                "name": "Custom Manufacturing",
                "code": "mrp_operation",
                "sequence_code": "CUSTOM-MO",
                "default_location_src_id": self.stock_location.id,
                "default_location_dest_id": self.stock_location.id,
                "production_location_id": self.custom_production_location.id,
            }
        )
        self.finished_product = self.product_model.create(
            {
                "name": "Finished Product",
                "type": "product",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.component_product = self.product_model.create(
            {
                "name": "Component Product",
                "type": "product",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.bom = self.bom_model.create(
            {
                "product_id": self.finished_product.id,
                "product_tmpl_id": self.finished_product.product_tmpl_id.id,
                "product_uom_id": self.finished_product.uom_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.component_product.id,
                            "product_qty": 2.0,
                        },
                    )
                ],
            }
        )

    def test_01_production_location_in_mo_and_moves(self):
        mo_form = Form(self.production_model)
        mo_form.product_id = self.finished_product
        mo_form.bom_id = self.bom
        mo_form.picking_type_id = self.custom_picking_type
        mo_form.product_qty = 1.0
        mo = mo_form.save()
        self.assertEqual(
            mo.production_location_id,
            self.custom_production_location,
            "Production location should be set from picking type",
        )
        raw_moves = mo.move_raw_ids
        self.assertTrue(raw_moves, "Raw material moves should exist")
        for move in raw_moves:
            self.assertEqual(
                move.location_dest_id,
                self.custom_production_location,
                f"Raw material move {move.product_id.name} should have "
                f"custom production location as destination",
            )
        finished_moves = mo.move_finished_ids
        self.assertTrue(finished_moves, "Finished product moves should exist")
        for move in finished_moves:
            self.assertEqual(
                move.location_id,
                self.custom_production_location,
                f"Finished product move {move.product_id.name} should have "
                f"custom production location as source",
            )

    def test_02_default_behavior_without_custom_location(self):
        default_picking_type = self.warehouse.manu_type_id
        mo_form = Form(self.production_model)
        mo_form.product_id = self.finished_product
        mo_form.bom_id = self.bom
        mo_form.picking_type_id = default_picking_type
        mo_form.product_qty = 1.0
        mo = mo_form.save()
        mo.action_confirm()
        self.assertNotEqual(
            mo.production_location_id,
            self.custom_production_location,
        )
        for move in mo.move_raw_ids:
            self.assertNotEqual(
                move.location_dest_id,
                self.custom_production_location,
            )
        for move in mo.move_finished_ids:
            self.assertNotEqual(
                move.location_id,
                self.custom_production_location,
            )
