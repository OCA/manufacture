from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestQualityControl(TransactionCase):
    def setUp(self):
        """
        Sets some enviroment
        """
        super(TestQualityControl, self).setUp()

        self.plan_model = self.env["qc.plan"]
        self.level_model = self.env["qc.level"]
        self.inspection_model = self.env["qc.inspection"]
        self.category_model = self.env["product.category"]
        self.Trigger_product_model = self.env["qc.trigger.product_template_line"]
        self.Trigger_category_model = self.env["qc.trigger.product_category_line"]
        self.Trigger_partner_model = self.env["qc.trigger.partner_line"]
        self.Partner_model = self.env["res.partner"]

        self.qc_trigger = self.env["qc.trigger"].create(
            {
                "name": "Test Trigger",
                "active": True,
            }
        )
        self.test = self.env.ref("quality_control_oca.qc_test_1")
        self.product = self.env.ref("product.product_product_10")
        self.product1 = self.env.ref("product.product_product_11")
        self.product2 = self.env.ref("product.product_product_12")
        self.product3 = self.env.ref("product.product_product_13")
        self.category = self.category_model.create({"name": "Plan test Category"})
        self.product1.categ_id = self.category.id

    def test_plan(self):
        """
        Test Plan
        """
        # creating plan
        plan1 = self.plan_model.create({"name": "Test", "free_pass": False})
        self.assertEqual(plan1.id > 0, True)
        self.assertEqual(plan1.name == "Test", True)
        self.assertEqual(plan1.free_pass is False, True)
        # assigning a level to the plan
        level = self.level_model.create(
            {
                "plan_id": plan1.id,
                "qty_received": 10,
                "qty_checked": 3,
                "chk_type": "percent",
            }
        )
        self.assertEqual(level.plan_id.id == plan1.id, True)

        # adding second free pass plan
        plan2 = self.plan_model.create({"name": "Test2", "free_pass": True})
        if plan2:
            plan3 = self.plan_model.create({"name": "Test3", "free_pass": True})
            self.assertEqual(plan3, False)

        # setting another plan as free pass
        plan3 = self.plan_model.create({"name": "Test3", "free_pass": False})
        plan3.free_pass = True
        with self.assertRaises(ValidationError) as ve:
            plan3.on_change_free_pass()
        self.assertIn("A free pass plan already exists", str(ve.exception))

        # create a the plan
        plan2.free_pass = False
        self.level_model.create(
            {
                "plan_id": plan2.id,
                "qty_received": 10,
                "qty_checked": 7,
                "chk_type": "absolute",
            }
        )

        partner = self.Partner_model.create({"name": "Plan test Partner"})

        # creating quality triggers
        trigger_product = self.Trigger_product_model.create(
            {
                "product_template": self.product.product_tmpl_id.id,
                "trigger": self.qc_trigger.id,
                "test": self.test.id,
                "plan_id": plan1.id,
            }
        )

        trigger_product_partner = self.Trigger_product_model.create(
            {
                "product_template": self.product.product_tmpl_id.id,
                "trigger": self.qc_trigger.id,
                "test": self.test.id,
                "plan_id": plan2.id,
            }
        )
        trigger_product_partner.partners = partner

        trigger_category = self.Trigger_category_model.create(
            {
                "product_category": self.category.id,
                "trigger": self.qc_trigger.id,
                "test": self.test.id,
                "plan_id": plan1.id,
            }
        )

        trigger_category_partner = self.Trigger_category_model.create(
            {
                "product_category": self.category.id,
                "trigger": self.qc_trigger.id,
                "test": self.test.id,
                "plan_id": plan1.id,
            }
        )
        trigger_category_partner.partners = partner

        trigger_partner = self.Trigger_partner_model.create(
            {"trigger": self.qc_trigger.id, "test": self.test.id, "plan_id": plan1.id}
        )
        trigger_partner.partner = partner

        self.assertEqual(trigger_product.id > 0, True)
        self.assertEqual(trigger_product_partner.id > 0, True)
        self.assertEqual(trigger_category.id > 0, True)
        self.assertEqual(trigger_category_partner.id > 0, True)
        self.assertEqual(trigger_partner.id > 0, True)

        # creates inspection for product
        # get a move and a picking
        get_move = self.env["stock.move"].search([])[0]
        get_picking = self.env["stock.picking"].search([])[0]
        # tests picking inherit
        picking_ck = get_picking._action_done()
        self.assertEqual(picking_ck, True)

        # creates inspection for free pass
        # adapt move's attributes with used data
        get_move.product_id = self.product.id
        obj_id = "stock.move," + str(get_move.id)
        plan1.free_pass = True
        self.inspection2 = self.inspection_model.create(
            {
                "object_id": obj_id,
                "state": "ready",
                "test": 1,
                "user": 1,
                "auto_generated": True,
                "qty": 300.0,
            }
        )
        self.assertEqual(self.inspection2.qty_checked == 0, True)

        # creates inspection for product
        plan1.free_pass = False
        self.inspection2 = self.inspection_model.create(
            {
                "object_id": obj_id,
                "state": "ready",
                "test": 1,
                "user": 1,
                "auto_generated": True,
                "qty": 300.0,
            }
        )
        self.assertEqual(self.inspection2.qty_checked == 9, True)

        # creates inspection for product partner
        get_move.picking_id = get_picking.id
        get_picking.partner_id = partner
        self.inspection2 = self.inspection_model.create(
            {
                "object_id": obj_id,
                "state": "ready",
                "test": 1,
                "user": 1,
                "auto_generated": True,
                "qty": 300.0,
            }
        )
        self.assertEqual(self.inspection2.qty_checked == 7, True)

        # creates inspection for category
        get_move.product_id = self.product1.id
        get_move.picking_id = False
        # self.product.category = self.category.id
        self.inspection2 = self.inspection_model.create(
            {
                "object_id": obj_id,
                "state": "ready",
                "test": 1,
                "user": 1,
                "auto_generated": True,
                "qty": 150.0,
            }
        )
        self.assertEqual(self.inspection2.qty_checked == 4, True)

        # creates inspection for partner
        # get a move from db
        get_move.product_id = self.product2.id
        get_move.picking_id = get_picking.id
        get_picking.partner_id = partner
        self.inspection2 = self.inspection_model.create(
            {
                "object_id": obj_id,
                "state": "ready",
                "test": 1,
                "user": 1,
                "auto_generated": True,
                "qty": 400.0,
            }
        )
        self.assertEqual(self.inspection2.qty_checked == 12, True)

        # create inspection without plan
        partner2 = self.Partner_model.create({"name": "Plan test Partner2"})
        get_move.product_id = self.product3.id
        get_move.picking_id = get_picking.id
        get_picking.partner_id = partner2
        self.inspection2 = self.inspection_model.create(
            {
                "object_id": obj_id,
                "state": "ready",
                "test": 1,
                "user": 1,
                "auto_generated": True,
                "qty": 400.0,
            }
        )
        self.assertEqual(self.inspection2.qty_checked == 1, True)
