# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form, common


class TestMRPUnbuildOriginLocation(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.custom_location = cls.env["stock.location"].create(
            {
                "name": "Custom Sub Location",
                "location_id": cls.stock_location.id,
                "usage": "internal",
            }
        )
        Product = cls.env["product.product"]
        BOM = cls.env["mrp.bom"]

        cls.component_product = Product.create(
            {
                "name": "Component Product",
                "type": "product",
            }
        )
        cls.tracking_product = Product.create(
            {
                "name": "Tracking Component",
                "type": "product",
                "tracking": "lot",
            }
        )
        cls.finished_product = Product.create(
            {
                "name": "Finished Product",
                "type": "product",
            }
        )
        cls.bom = BOM.create(
            {
                "product_tmpl_id": cls.finished_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.component_product.id,
                            "product_qty": 1.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.tracking_product.id,
                            "product_qty": 1.0,
                        }
                    ),
                ],
            }
        )
        cls.owner = cls.env["res.partner"].create({"name": "Test Owner"})
        quant1 = cls.env["stock.quant"].create(
            {
                "location_id": cls.custom_location.id,
                "product_id": cls.component_product.id,
                "owner_id": cls.owner.id,
                "inventory_quantity": 10,
            }
        )
        quant1.action_apply_inventory()
        cls.lot = cls.env["stock.lot"].create(
            {
                "product_id": cls.tracking_product.id,
                "name": "LOT-001",
            }
        )
        quant2 = cls.env["stock.quant"].create(
            {
                "location_id": cls.custom_location.id,
                "product_id": cls.tracking_product.id,
                "lot_id": cls.lot.id,
                "inventory_quantity": 10,
            }
        )
        quant2.action_apply_inventory()

    def _create_mo(self):
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.finished_product.id,
                "product_qty": 1.0,
                "bom_id": self.bom.id,
            }
        )
        mo.action_confirm()
        mark_done_action = mo.button_mark_done()
        tracking_move = mo.move_raw_ids.filtered(
            lambda m: m.product_id == self.tracking_product
        )
        tracking_move.quantity_done = 1.0
        tracking_move.move_line_ids.write(
            {
                "lot_id": self.lot.id,
                "qty_done": 1.0,
            }
        )
        immediate_production_wizard = Form(
            self.env["mrp.immediate.production"].with_context(
                **mark_done_action["context"]
            )
        ).save()
        immediate_production_wizard.process()
        return mo

    def _create_unbuild(self, mo, restore_rm_stock=False):
        unbuild = self.env["mrp.unbuild"].create(
            {
                "mo_id": mo.id,
                "product_id": self.finished_product.id,
                "product_qty": 1.0,
                "restore_rm_stock_in_origin_loc": restore_rm_stock,
            }
        )
        unbuild.action_unbuild()
        return unbuild

    def test_unbuild_with_restore_rm_stock_true(self):
        mo = self._create_mo()
        unbuild = self._create_unbuild(mo, restore_rm_stock=True)
        move_lines = self.env["stock.move.line"].search(
            [("reference", "=", unbuild.name)]
        )
        for line in move_lines.filtered(
            lambda l: l.product_id in [self.component_product, self.tracking_product]
        ):
            self.assertEqual(line.location_dest_id, self.custom_location)

    def test_unbuild_with_restore_rm_stock_false(self):
        mo = self._create_mo()
        unbuild = self._create_unbuild(mo, restore_rm_stock=False)
        move_lines = self.env["stock.move.line"].search(
            [("reference", "=", unbuild.name)]
        )
        for line in move_lines.filtered(
            lambda l: l.product_id in [self.component_product, self.tracking_product]
        ):
            self.assertNotEqual(line.location_dest_id, self.custom_location)

    def test_unbuild_preserves_owner_id(self):
        mo = self._create_mo()
        unbuild = self._create_unbuild(mo, restore_rm_stock=True)
        move_lines = self.env["stock.move.line"].search(
            [("reference", "=", unbuild.name)]
        )
        owner_move_line = move_lines.filtered(
            lambda l: l.product_id == self.component_product
        )
        self.assertTrue(
            owner_move_line, "No move lines found for the component product"
        )
        self.assertEqual(owner_move_line.owner_id, self.owner)
