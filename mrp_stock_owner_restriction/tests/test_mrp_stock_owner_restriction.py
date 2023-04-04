# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestMrpStockOwnerRestriction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.manufacture_route = cls.env.ref("mrp.route_warehouse0_manufacture")

        cls.finished_product = cls.env["product.product"].create(
            {"name": "test product", "type": "product"}
        )
        cls.component = cls.env["product.product"].create(
            {"name": "test component", "type": "product"}
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_id": cls.finished_product.id,
                "product_tmpl_id": cls.finished_product.product_tmpl_id.id,
                "product_uom_id": cls.finished_product.uom_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )
        cls.env["mrp.bom.line"].create(
            {"bom_id": cls.bom.id, "product_id": cls.component.id, "product_qty": 1}
        )
        cls.owner = cls.env["res.partner"].create({"name": "Owner test"})
        cls.finished_product.route_ids = [(6, 0, cls.manufacture_route.ids)]
        cls.picking_type = cls.env["stock.picking.type"].search(
            [
                ("code", "=", "mrp_operation"),
                ("warehouse_id.company_id", "=", cls.company.id),
            ],
            limit=1,
        )
        cls.picking_type.write({"owner_restriction": "picking_partner"})
        quant_vals = {
            "product_id": cls.component.id,
            "location_id": cls.picking_type.default_location_src_id.id,
            "quantity": 250.00,
        }
        # Create quants without owner
        cls.env["stock.quant"].create(quant_vals)
        # Create quants with owner
        cls.env["stock.quant"].create(dict(quant_vals, owner_id=cls.owner.id))

    def test_mrp_quant_assign_owner(self):
        self.assertEqual(self.component.qty_available, 250)
        self.component.invalidate_model(["qty_available"])
        self.assertEqual(
            self.component.with_context(skip_restricted_owner=True).qty_available, 500
        )
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.finished_product.id,
                "bom_id": self.bom.id,
                "product_qty": 250,
                "picking_type_id": self.picking_type.id,
                "owner_id": self.owner.id,
            }
        )
        mo.action_confirm()
        action = mo.button_mark_done()
        self.assertEqual(action.get("res_model"), "mrp.immediate.production")
        wizard = Form(
            self.env[action["res_model"]].with_context(**action["context"])
        ).save()
        action = wizard.process()

        # Check produced product owner and qty_available
        self.assertEqual(self.finished_product.qty_available, 0.00)
        self.finished_product.invalidate_model(["qty_available"])
        self.assertEqual(
            self.finished_product.with_context(
                skip_restricted_owner=True
            ).qty_available,
            250.00,
        )
        quant = self.env["stock.quant"].search(
            [("product_id", "=", self.finished_product.id)]
        )
        self.assertEqual(quant.owner_id, self.owner)

        # Confirm that component inventory with owner has been consumed
        self.assertEqual(self.component.qty_available, 250)
        self.component.invalidate_model(["qty_available"])
        self.assertEqual(
            self.component.with_context(skip_restricted_owner=True).qty_available, 250
        )
