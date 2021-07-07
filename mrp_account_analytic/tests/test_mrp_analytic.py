from odoo.tests import Form, common


class TestMRP(common.TransactionCase):
    """
    Create a Manufacturing Order, with Raw Materials and Operations.
    Consuming raw materials generates or updates Analytic Items.
    Working on Operations generates or updates Analytic Items.
    """

    def setUp(self):
        super().setUp()
        # Analytic Account
        self.analytic_1 = self.env["account.analytic.account"].create({"name": "Job 1"})
        # Work Center
        self.mrp_workcenter_1 = self.env["mrp.workcenter"].create(
            {
                "name": "Assembly Line",
                "costs_hour": 40,
            }
        )
        # Products
        self.product_lemonade = self.env["product.product"].create(
            {
                "name": "Lemonade",
                "type": "product",
                "standard_price": 20,
            }
        )
        self.product_lemon = self.env["product.product"].create(
            {
                "name": "Lemon",
                "type": "product",
                "standard_price": 1,
            }
        )
        # BOM
        self.mrp_bom_lemonade = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product_lemonade.product_tmpl_id.id,
                "operation_ids": [
                    (
                        0,
                        0,
                        {
                            "workcenter_id": self.mrp_workcenter_1.id,
                            "name": "Squeeze Lemons",
                            "time_cycle": 15,
                        },
                    ),
                ],
            }
        )
        self.mrp_bom_lemonade.write(
            {
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_lemon.id,
                            "product_qty": 4,
                        },
                    )
                ]
            }
        )
        # MO
        mo_create_form = Form(self.env["mrp.production"])
        mo_create_form.product_id = self.product_lemonade
        mo_create_form.bom_id = self.mrp_bom_lemonade
        mo_create_form.product_qty = 1
        self.mo_lemonade = mo_create_form.save()
        self.mo_lemonade.analytic_account_id = self.analytic_1
        self.mo_lemonade.action_confirm()

    def test_100_one_step_produce(self):
        # Form edit the MO and Save
        mo_form = Form(self.mo_lemonade)
        mo_form.qty_producing = 1
        mo_lemonade = mo_form.save()
        # Set 15 minutes to work time and "Mark As Done"
        mo_lemonade.workorder_ids.duration = 15
        mo_lemonade.button_mark_done()

        analytic_items = self.env["account.analytic.line"].search(
            [("manufacturing_order_id", "=", mo_lemonade.id)]
        )
        # Expected (4 * 1.00) + (0.25 * 40.00) => 14.00
        analytic_qty = sum(analytic_items.mapped("unit_amount"))
        self.assertEqual(analytic_qty, 4.25, "Expected Analytic Items total quantity")
        analytic_amount = sum(analytic_items.mapped("amount"))
        self.assertEqual(
            analytic_amount, -14.00, "Expected Analytic Items total amount"
        )

    def test_110_two_step_produce(self):
        # Consume some raw material
        self.mo_lemonade.move_raw_ids.write({"quantity_done": 1})
        self.mo_lemonade.move_raw_ids.write({"quantity_done": 2})
        self.mo_lemonade.move_raw_ids.write({"quantity_done": 4})
        # Work on operations up to 15 minutes
        self.mo_lemonade.workorder_ids.write({"duration": 5})
        self.mo_lemonade.workorder_ids.write({"duration": 10})
        self.mo_lemonade.workorder_ids.write({"duration": 15})

        analytic_items = self.env["account.analytic.line"].search(
            [("manufacturing_order_id", "=", self.mo_lemonade.id)]
        )
        # Expected (4 * 1.00) + (0.25 * 40.00) => 14.00
        analytic_qty = sum(analytic_items.mapped("unit_amount"))
        self.assertEqual(analytic_qty, 4.25, "Expected Analytic Items total quantity")
        analytic_amount = sum(analytic_items.mapped("amount"))
        self.assertEqual(
            analytic_amount, -14.00, "Expected Analytic Items total amount"
        )
