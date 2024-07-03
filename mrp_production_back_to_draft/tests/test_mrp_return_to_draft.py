# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api
from odoo.exceptions import UserError
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestMrpProductionAutovalidate(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestMrpProductionAutovalidate, cls).setUpClass()
        cls.user_admin = cls.env.ref("base.user_admin")
        cls.env = api.Environment(cls.cr, cls.user_admin.id, {})
        cls.env.user.tz = False  # Make sure there's no timezone in user
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.env.user.write(
            {
                "groups_id": [
                    (6, 0, cls.env.user.groups_id.ids),
                    (4, cls.env.ref("stock.group_stock_manager").id),
                ],
            }
        )
        cls.prod_tp1 = cls.env["product.product"].create(
            {
                "name": "Test Product 1",
                "type": "product",
            }
        )
        cls.prod_ti1 = cls.env["product.product"].create(
            {
                "name": "Test Product Intermediate 1",
                "type": "product",
            }
        )
        # Create BoMs:
        cls.test_bom_1 = cls.env["mrp.bom"].create(
            {
                "product_id": cls.prod_tp1.id,
                "product_tmpl_id": cls.prod_tp1.product_tmpl_id.id,
                "product_uom_id": cls.prod_tp1.uom_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )
        cls.env["mrp.bom.line"].create(
            {
                "bom_id": cls.test_bom_1.id,
                "product_id": cls.prod_ti1.id,
                "product_qty": 1.0,
            }
        )
        cls.mo_1 = cls.env["mrp.production"].create(
            {
                "name": "MO ABC",
                "product_id": cls.prod_tp1.id,
                "product_uom_id": cls.prod_tp1.uom_id.id,
                "product_qty": 2,
                "bom_id": cls.test_bom_1.id,
            }
        )

    def test_01_mrp_return_to_draft(self):
        self.env["stock.quant"]._update_available_quantity(
            self.prod_ti1, self.location, 2
        )
        self.assertEqual(self.mo_1.state, "draft")
        self.mo_1._onchange_move_raw()
        self.mo_1.action_confirm()
        self.assertEqual(self.mo_1.state, "confirmed")
        self.mo_1.action_return_to_draft()
        self.assertEqual(self.mo_1.state, "draft")
        self.mo_1._onchange_move_raw()
        self.mo_1.action_confirm()
        self.assertEqual(self.mo_1.state, "confirmed")
        self.mo_1.action_cancel()
        self.assertEqual(self.mo_1.state, "cancel")
        self.mo_1.action_return_to_draft()
        self.assertEqual(self.mo_1.state, "draft")
        self.mo_1._onchange_move_raw()
        self.mo_1.action_confirm()
        self.mo_1.qty_producing = 2
        self.assertEqual(self.mo_1.state, "to_close")
        with self.assertRaises(UserError):
            self.mo_1.action_return_to_draft()
