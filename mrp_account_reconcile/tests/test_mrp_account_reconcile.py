from odoo.tests import Form

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestMrpAccountReconcile(TestMrpCommon):
    def setUp(self):
        super(TestMrpAccountReconcile, self).setUp()
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.env.ref("base.group_user").write(
            {"implied_ids": [(4, self.env.ref("stock.group_production_lot").id)]}
        )
        self.account = self.env["account.account"].create(
            {
                "name": "Manufacturing Wip",
                "code": "TestAccount",
                "user_type_id": self.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
            }
        )

        self.location = self.env["stock.location"].search(
            [("usage", "=", "production")]
        )
        self.location.valuation_in_account_id = self.account.id
        self.location.valuation_out_account_id = self.account.id
        self.pc = self.env["product.category"].create(
            {
                "name": "Category test",
                "property_valuation": "real_time",
                "property_cost_method": "fifo",
            }
        )

    def test_mrp_reconcile(self):
        """This test creates a Manufacturing order, then validates that the
        account Manufacturing Wip is reconciled."""

        mo, bom, p_final, p1, p2 = self.generate_mo(
            qty_final=1, qty_base_1=1, qty_base_2=1
        )

        p1.categ_id = self.pc.id
        p2.categ_id = self.pc.id
        p_final.categ_id = self.pc.id

        p1.standard_price = 10
        p2.standard_price = 5

        self.env["stock.quant"]._update_available_quantity(p1, self.stock_location, 1)
        self.env["stock.quant"]._update_available_quantity(p2, self.stock_location, 1)
        mo.action_assign()

        # We create a manufacturing order that has the cost of 10+5 = 15
        mo_form = Form(mo)
        mo_form.qty_producing = 1
        mo = mo_form.save()
        mo.button_mark_done()

        self.assertEqual(
            p_final.free_qty,
            1,
            "You should have 1 final product available",
        )
        self.assertEqual(
            p_final.standard_price,
            15,
            "The standard price of the final product should be 15",
        )

        # We check that the movements of the production account have been reconciled
        move_line_reconciled = mo.account_move_line_ids.filtered(
            lambda x: x.account_id == self.account and x.reconciled
        )
        self.assertEqual(
            len(move_line_reconciled),
            3,
            "The account movements should be 3",
        )
        self.assertEqual(
            move_line_reconciled[0].balance,
            -15,
            "The balance of the account movement should be -15",
        )
        self.assertEqual(
            move_line_reconciled[1].balance,
            10,
            "The balance of the account movement should be 10",
        )
        self.assertEqual(
            move_line_reconciled[2].balance,
            5,
            "The balance of the account movement should be 5",
        )

    def test_unbuild_reconcile(self):
        """This test creates an Unbuild order from a Manufacturing order,
        then validates that the account Manufacturing Wip is reconciled."""

        mo, bom, p_final, p1, p2 = self.generate_mo(
            qty_final=1, qty_base_1=1, qty_base_2=1
        )

        p1.categ_id = self.pc.id
        p2.categ_id = self.pc.id
        p_final.categ_id = self.pc.id

        p1.standard_price = 10
        p2.standard_price = 5

        self.env["stock.quant"]._update_available_quantity(p1, self.stock_location, 1)
        self.env["stock.quant"]._update_available_quantity(p2, self.stock_location, 1)
        mo.action_assign()

        # We create a manufacturing order that has the cost of 10+5 = 15
        mo_form = Form(mo)
        mo_form.qty_producing = 1
        mo = mo_form.save()
        mo.button_mark_done()

        # We make the unbuild of the manufacturing order
        a = mo.button_unbuild()
        unbuild = self.env["mrp.unbuild"].create(
            {
                "product_id": a["context"]["default_product_id"],
                "mo_id": a["context"]["default_mo_id"],
                "company_id": a["context"]["default_company_id"],
                "location_id": a["context"]["default_location_id"],
                "location_dest_id": a["context"]["default_location_dest_id"],
                "product_uom_id": mo["product_uom_id"].id,
                "product_qty": 1,
            }
        )
        unbuild.action_validate()

        # We check that the movements of the production account have been reconciled
        move_line_reconciled = unbuild.account_move_line_ids.filtered(
            lambda x: x.account_id == self.account and x.reconciled
        )
        self.assertEqual(
            len(move_line_reconciled),
            3,
            "The account movements should be 3",
        )
        self.assertEqual(
            move_line_reconciled[0].balance,
            -10,
            "The balance of the account movement should be -10",
        )
        self.assertEqual(
            move_line_reconciled[1].balance,
            -5,
            "The balance of the account movement should be -5",
        )
        self.assertEqual(
            move_line_reconciled[2].balance,
            15,
            "The balance of the account movement should be 15",
        )
