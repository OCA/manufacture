from odoo.tests import Form

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestMrpOrder(TestMrpCommon):
    def setUp(self):
        super(TestMrpOrder, self).setUp()
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.env.ref("base.group_user").write(
            {"implied_ids": [(4, self.env.ref("stock.group_production_lot").id)]}
        )

    def test_mrp_with_journal_items(self):
        """This test creates a Manufacturing orderand then check if the
        Journal Items button links to the journal items of the order.
        """
        journal_items_before_production = self.env["account.move.line"].search([]).ids

        mo, bom, p_final, p1, p2 = self.generate_mo()
        account = self.env["account.account"].create(
            {
                "name": "Test Account",
                "code": "TestAccount1",
                "user_type_id": self.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
            }
        )
        location = self.env["stock.location"].search([("usage", "=", "production")])
        location.valuation_in_account_id = account.id
        location.valuation_out_account_id = account.id
        pc = self.env["product.category"].create(
            {
                "name": "Category test",
                "property_valuation": "real_time",
                "property_cost_method": "fifo",
            }
        )
        p1.categ_id = pc.id
        p1.standard_price = 10
        p2.categ_id = pc.id
        p2.standard_price = 5
        p_final.categ_id = pc.id

        self.env["stock.quant"]._update_available_quantity(p1, self.stock_location, 100)
        self.env["stock.quant"]._update_available_quantity(p2, self.stock_location, 5)
        mo.action_assign()

        mo_form = Form(mo)
        mo_form.qty_producing = 5.0
        mo = mo_form.save()
        mo.button_mark_done()

        journal_items_after_production = self.env["account.move.line"].search([]).ids

        result = mo.view_journal_items()
        domain = result["domain"]
        mo_journal_items = list(domain[0][2])
        difference_journal_items = list(
            set(journal_items_after_production) - set(journal_items_before_production)
        )
        mo_journal_items.sort()
        difference_journal_items.sort()

        self.assertTrue(
            difference_journal_items,
            "There should be new journal items after doing the manufacturing order",
        )
        self.assertEqual(
            result["res_model"],
            "account.move.line",
            "You should access to the model account.move.line",
        )
        self.assertEqual(
            difference_journal_items,
            mo_journal_items,
            "You should have as domain the ids of the journal items",
        )


class TestUnbuild(TestMrpCommon):
    def setUp(self):
        super(TestUnbuild, self).setUp()
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.env.ref("base.group_user").write(
            {"implied_ids": [(4, self.env.ref("stock.group_production_lot").id)]}
        )

    def test_unbuild_with_journal_items(self):
        """This test creates an Unbuild order from a Manufacturing order and then check if the
        Journal Items button links to the journal items of the order.
        """

        mo, bom, p_final, p1, p2 = self.generate_mo()
        account = self.env["account.account"].create(
            {
                "name": "Test Account",
                "code": "TestAccount2",
                "user_type_id": self.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
            }
        )
        location = self.env["stock.location"].search([("usage", "=", "production")])
        location.valuation_in_account_id = account.id
        location.valuation_out_account_id = account.id
        pc = self.env["product.category"].create(
            {
                "name": "Category test",
                "property_valuation": "real_time",
                "property_cost_method": "fifo",
            }
        )
        p1.categ_id = pc.id
        p1.standard_price = 10
        p2.categ_id = pc.id
        p2.standard_price = 5
        p_final.categ_id = pc.id

        self.env["stock.quant"]._update_available_quantity(p1, self.stock_location, 100)
        self.env["stock.quant"]._update_available_quantity(p2, self.stock_location, 5)
        mo.action_assign()

        mo_form = Form(mo)
        mo_form.qty_producing = 5.0
        mo = mo_form.save()
        mo.button_mark_done()
        journal_items_before_unbuild = self.env["account.move.line"].search([]).ids

        x = Form(self.env["mrp.unbuild"])
        x.product_id = p_final
        x.bom_id = bom
        x.product_qty = 5
        unbuild = x.save()
        unbuild.action_unbuild()
        journal_items_after_unbuild = self.env["account.move.line"].search([]).ids

        result = unbuild.view_journal_items()
        domain = result["domain"]
        unbuild_journal_items = domain[0][2]
        difference_journal_items = list(
            set(journal_items_after_unbuild) - set(journal_items_before_unbuild)
        )
        unbuild_journal_items.sort()
        difference_journal_items.sort()

        self.assertTrue(
            difference_journal_items,
            "There should be new journal items after doing the unbuild",
        )
        self.assertEqual(
            result["res_model"],
            "account.move.line",
            "You should access to the model account.move.line",
        )
        self.assertEqual(
            difference_journal_items,
            unbuild_journal_items,
            "You should have as domain the ids of the journal items",
        )
