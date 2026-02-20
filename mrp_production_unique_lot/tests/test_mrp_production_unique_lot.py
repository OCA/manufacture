# Copyright 2025 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import Form

from odoo.addons.mrp.tests import common


class TestMrpLotUniqueness(common.TestMrpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.picking_type = cls.env.ref("stock.warehouse0").manu_type_id
        cls.picking_type.write({"force_production_lot_uniqueness": True})
        cls.mo, cls.bom, cls.final_product, _, _ = cls.generate_mo(
            tracking_final="lot", picking_type_id=cls.picking_type
        )
        cls.lot = cls.env["stock.lot"].create(
            {"name": "LOT-001", "product_id": cls.final_product.id}
        )

        cls.byproduct = cls.env["product.product"].create(
            {"name": "Byproduct", "is_storable": True, "tracking": "lot"}
        )
        cls.bom_byproduct = cls.bom.copy(
            {
                "byproduct_ids": [
                    Command.create(
                        {
                            "product_id": cls.byproduct.id,
                            "product_qty": 1,
                            "product_uom_id": cls.byproduct.uom_id.id,
                        }
                    )
                ]
            }
        )

        mo_form = Form(cls.mo)
        mo_form.qty_producing = 5
        mo = mo_form.save()
        mo.lot_producing_ids = cls.lot
        mo.button_mark_done()

    def test_unique_lot_validation(self):
        mo2 = self.env["mrp.production"].create(
            {
                "product_id": self.final_product.id,
                "bom_id": self.bom.id,
                "picking_type_id": self.picking_type.id,
                "product_qty": 10,
            }
        )
        mo2.action_confirm()
        self.assertNotIn(self.lot, mo2.allowed_lot_producing_ids)

        # Try to assign the same lot
        mo_form = Form(mo2)
        mo_form.qty_producing = 10
        mo_form.lot_producing_ids = self.lot
        mo = mo_form.save()
        with self.assertRaises(UserError):
            mo.button_mark_done()

        # Try with another lot
        lot2 = self.env["stock.lot"].create(
            {"name": "LOT-002", "product_id": self.final_product.id}
        )
        mo2.action_clear_lot_producing_ids()
        mo_form = Form(mo2)
        mo_form.qty_producing = 10
        mo_form.lot_producing_ids = lot2
        mo = mo_form.save()
        mo.button_mark_done()

    def test_lot_reusable_after_unbuild(self):
        x = Form(self.env["mrp.unbuild"])
        x.product_id = self.final_product
        x.mo_id = self.mo
        x.lot_id = self.lot
        x.product_qty = self.mo.product_qty
        x.save().action_unbuild()

        mo2 = self.env["mrp.production"].create(
            {
                "product_id": self.final_product.id,
                "bom_id": self.bom.id,
                "picking_type_id": self.picking_type.id,
                "product_qty": 10,
            }
        )
        mo2.action_confirm()
        self.assertIn(self.lot, mo2.allowed_lot_producing_ids)

        # Try to assign the same lot, it should not raise
        mo_form = Form(mo2)
        mo_form.qty_producing = 10
        mo_form.lot_producing_ids = self.lot
        mo = mo_form.save()
        mo.button_mark_done()

    def test_lot_reusable_after_scrap(self):
        scrap_id = (
            self.env["stock.scrap"]
            .with_context(active_model="mrp.production", active_id=self.mo.id)
            .create(
                {
                    "product_id": self.final_product.id,
                    "scrap_qty": self.mo.product_qty,
                    "product_uom_id": self.final_product.uom_id.id,
                    "production_id": self.mo.id,
                    "lot_id": self.lot.id,
                }
            )
        )
        scrap_id.do_scrap()

        mo2 = self.env["mrp.production"].create(
            {
                "product_id": self.final_product.id,
                "bom_id": self.bom.id,
                "picking_type_id": self.picking_type.id,
                "product_qty": 10,
            }
        )
        mo2.action_confirm()

        # Try to assign the same lot, it should not raise
        mo_form = Form(mo2)
        mo_form.qty_producing = 10
        mo_form.lot_producing_ids = self.lot
        mo = mo_form.save()
        mo.button_mark_done()

    def test_byproduct_lot_uniqueness(self):
        bp_lot = self.env["stock.lot"].create(
            {"name": "BP-LOT", "product_id": self.byproduct.id}
        )

        def produce(bp_qty):
            mo = self.env["mrp.production"].create(
                {
                    "product_id": self.final_product.id,
                    "bom_id": self.bom_byproduct.id,
                    "picking_type_id": self.picking_type.id,
                    "product_qty": 1,
                }
            )
            mo.action_confirm()
            mo_form = Form(mo)
            mo_form.qty_producing = 1
            mo = mo_form.save()
            mo.lot_producing_ids = self.env["stock.lot"].create(
                {"name": f"FIN-{mo.id}", "product_id": self.final_product.id}
            )
            move_bp = mo.move_finished_ids.filtered(
                lambda m: m.product_id == self.byproduct
            )
            move_bp.move_line_ids.write({"lot_id": bp_lot.id, "quantity": bp_qty})
            mo.button_mark_done()

        produce(1)
        with self.subTest("zero quantity line is skipped"):
            produce(0)
        with self.subTest("already produced lot"), self.assertRaises(UserError):
            produce(1)
