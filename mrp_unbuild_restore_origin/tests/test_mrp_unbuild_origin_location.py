# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import common


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
        cls.component_product = cls.env["product.product"].create(
            {
                "name": "Component",
                "is_storable": True,
            }
        )
        cls.finished_product = cls.env["product.product"].create(
            {
                "name": "Finished Product",
                "is_storable": True,
            }
        )
        cls.bom = cls.env["mrp.bom"].create(
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
                ],
            }
        )
        quant1 = cls.env["stock.quant"].create(
            {
                "location_id": cls.custom_location.id,
                "product_id": cls.component_product.id,
                "inventory_quantity": 10,
            }
        )
        quant1.action_apply_inventory()

    def _create_mo(self):
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.finished_product.id,
                "product_qty": 1.0,
                "bom_id": self.bom.id,
            }
        )
        mo.action_confirm()
        mo.button_mark_done()
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
            lambda ml: ml.product_id == self.component_product
        ):
            self.assertEqual(line.location_dest_id, self.custom_location)

    def test_unbuild_with_restore_rm_stock_false(self):
        mo = self._create_mo()
        unbuild = self._create_unbuild(mo, restore_rm_stock=False)
        move_lines = self.env["stock.move.line"].search(
            [("reference", "=", unbuild.name)]
        )
        for line in move_lines.filtered(
            lambda ml: ml.product_id == self.component_product
        ):
            self.assertNotEqual(line.location_dest_id, self.custom_location)
