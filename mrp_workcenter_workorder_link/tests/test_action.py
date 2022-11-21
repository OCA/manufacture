from odoo.tests.common import TransactionCase


class ExecuteButton(TransactionCase):
    def test_button_workcenter_line(self):
        workcenter = self.env.ref("mrp.mrp_workcenter_2")
        res = workcenter.button_workcenter_line()
        self.assertEqual(res["view_mode"], "tree,form")
        self.assertEqual(res["res_model"], "mrp.workorder")
        self.assertEqual(
            res["domain"],
            [
                ("state", "in", ("pending", "waiting", "ready", "progress")),
                ("workcenter_id", "in", workcenter.ids),
            ],
        )

    def test_button_workcenter(self):
        # easy way to generate an operation as there are not by default
        self.env["mrp.routing.workcenter"].with_context(active_test=False).search(
            []
        ).active = True
        self.env["mrp.production"].create(
            {
                "product_id": self.env.ref("mrp.product_product_computer_desk_head").id,
            }
        )
        workorder = self.env["mrp.workorder"].search([], limit=1)
        res = workorder.button_workcenter()
        self.assertEqual(res["view_mode"], "form")
        self.assertEqual(res["res_id"], workorder.workcenter_id.id)
