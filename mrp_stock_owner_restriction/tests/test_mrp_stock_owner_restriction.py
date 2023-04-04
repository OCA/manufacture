# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMrpStockOwnerRestriction(TransactionCase):
    def setUp(self):
        super(TestMrpStockOwnerRestriction, self).setUp()
        self.company = self.env.ref("base.main_company")
        self.manufacture_route = self.env.ref("mrp.route_warehouse0_manufacture")

        self.product = self.env["product.product"].create(
            {
                "name": "test product",
                "type": "product",
            }
        )
        self.product_2 = self.env["product.product"].create(
            {"name": "test component", "default_code": "PRD 2", "type": "product"}
        )
        self.bom = self.env["mrp.bom"].create(
            {
                "product_id": self.product.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "product_uom_id": self.product.uom_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )
        self.env["mrp.bom.line"].create(
            {"bom_id": self.bom.id, "product_id": self.product_2.id, "product_qty": 2}
        )
        self.owner = self.env["res.partner"].create({"name": "Owner test"})
        self.product.route_ids = [(6, 0, self.manufacture_route.ids)]
        self.picking_type_id = self.env["stock.picking.type"].search(
            [
                ("code", "=", "mrp_operation"),
                ("warehouse_id.company_id", "=", self.company.id),
            ],
            limit=1,
        )
        quant_vals = {
            "product_id": self.product_2.id,
            "location_id": self.picking_type_id.default_location_src_id.id,
            "quantity": 250.00,
        }
        # Create quants without owner
        self.env["stock.quant"].create(quant_vals)
        # Create quants with owner
        self.env["stock.quant"].create(dict(quant_vals, owner_id=self.owner.id))

    def test_mrp_quant_assign_owner(self):
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "bom_id": self.bom.id,
                "product_qty": 250,
                "picking_type_id": self.picking_type_id.id,
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
        self.assertEqual(self.product.qty_available, 0.00)
        self.product.invalidate_model()
        self.assertEqual(
            self.product.with_context(skip_restricted_owner=True).qty_available, 250.00
        )
        quant = self.env["stock.quant"].search([("product_id", "=", self.product.id)])
        self.assertEqual(quant.owner_id, self.owner)

        # Check component product qty_available
        self.assertEqual(self.product_2.qty_available, 0.00)
        self.product.invalidate_model()
        self.assertEqual(
            self.product_2.with_context(skip_restricted_owner=True).qty_available, 0.00
        )
