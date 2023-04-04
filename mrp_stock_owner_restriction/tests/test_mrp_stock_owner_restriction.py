# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMrpStockOwnerRestriction(TransactionCase):
    def setUp(self):
        super(TestMrpStockOwnerRestriction, self).setUp()
        self.company = self.env.ref("base.main_company")
        self.manufacture_route = self.env.ref("mrp.route_warehouse0_manufacture")

        self.finished_product = self.env["product.product"].create(
            {"name": "test product", "type": "product"}
        )
        self.component = self.env["product.product"].create(
            {"name": "test component", "type": "product"}
        )
        self.bom = self.env["mrp.bom"].create(
            {
                "product_id": self.finished_product.id,
                "product_tmpl_id": self.finished_product.product_tmpl_id.id,
                "product_uom_id": self.finished_product.uom_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )
        self.env["mrp.bom.line"].create(
            {"bom_id": self.bom.id, "product_id": self.component.id, "product_qty": 1}
        )
        self.owner = self.env["res.partner"].create({"name": "Owner test"})
        self.finished_product.route_ids = [(6, 0, self.manufacture_route.ids)]
        self.picking_type = self.env["stock.picking.type"].search(
            [
                ("code", "=", "mrp_operation"),
                ("warehouse_id.company_id", "=", self.company.id),
            ],
            limit=1,
        )
        self.picking_type.write({"owner_restriction": "picking_partner"})
        quant_vals = {
            "product_id": self.component.id,
            "location_id": self.picking_type.default_location_src_id.id,
            "quantity": 250.00,
        }
        # Create quants without owner
        self.env["stock.quant"].create(quant_vals)
        # Create quants with owner
        self.env["stock.quant"].create(dict(quant_vals, owner_id=self.owner.id))

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
