# Copyright 2024 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMrpMtoAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestMrpMtoAnalytic, cls).setUpClass()
        # Get the MTO route and activate it if necessary
        mto_route = cls.env.ref("stock.route_warehouse0_mto")
        manufacture_route = cls.env.ref("mrp.route_warehouse0_manufacture")
        if not mto_route.active:
            mto_route.write({"active": True})
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "product",
                "route_ids": [(6, 0, [mto_route.id, manufacture_route.id])],
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
                "type": "product",
                "route_ids": [(6, 0, [mto_route.id, manufacture_route.id])],
            }
        )
        cls.product3 = cls.env["product.product"].create(
            {"name": "Product 3", "type": "product"}
        )
        # Create BOMs for each product
        cls.bom1 = cls.env["mrp.bom"].create(
            {
                "product_id": cls.product1.id,
                "product_tmpl_id": cls.product1.product_tmpl_id.id,
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.product2.id, "product_qty": 1})
                ],
            }
        )
        cls.bom2 = cls.env["mrp.bom"].create(
            {
                "product_id": cls.product2.id,
                "product_tmpl_id": cls.product2.product_tmpl_id.id,
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.product3.id, "product_qty": 1})
                ],
            }
        )
        analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "Plan Test", "company_id": False}
        )
        analytic_account_manual = cls.env["account.analytic.account"].create(
            {"name": "manual", "plan_id": analytic_plan.id}
        )
        cls.analytic_distribution_manual = {str(analytic_account_manual.id): 100}

    def test_mo_analytic(self):
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product1.id,
                "product_qty": 1,
                "bom_id": self.bom1.id,
                "product_uom_id": self.product1.uom_id.id,
                "analytic_distribution": self.analytic_distribution_manual,
            }
        )
        # Confirm MO to trigger child MO creation
        mo.action_confirm()
        # Find the child MO for the second product
        child_mo = mo._get_children()
        # Test if the analytic_distribution of MO and child MO are the same
        self.assertEqual(mo.analytic_distribution, self.analytic_distribution_manual)
        self.assertEqual(
            child_mo.analytic_distribution,
            mo.analytic_distribution,
            "Ananlytic Distributions do not match",
        )
