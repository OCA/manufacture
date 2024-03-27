from odoo import exceptions
from odoo.tests import Form, common, tagged


@tagged("post_install", "-at_install")
class TestSubcontractedPartner(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_id = cls.env.ref("base.res_partner_12")
        cls.partner_obj = cls.env["res.partner"]
        form = Form(cls.env["stock.warehouse"])
        form.name = "Warehouse #1"
        form.code = "WH#1"
        cls.warehouse1 = form.save()

        form = Form(cls.env["stock.warehouse"])
        form.name = "Warehouse #2"
        form.code = "WH#2"
        cls.warehouse2 = form.save()

        form = Form(cls.env["stock.warehouse"])
        form.name = "Warehouse #3"
        form.code = "WH#3"
        cls.warehouse3 = form.save()

    def test_is_subcontractor_partner_first_time(self):
        self.partner_id.update(
            {
                "is_subcontractor_partner": True,
            }
        )

        location = self.partner_id.subcontracted_created_location_id
        self.assertTrue(location, "Location is not created")
        self.assertTrue(location.active, "Location must be active")

        partner_picking_type = self.partner_id.partner_picking_type_id
        self.assertTrue(partner_picking_type, "Picking type is not created")
        self.assertTrue(partner_picking_type.active, "Picking type must be active")

        partner_buy_rule = self.partner_id.partner_buy_rule_id
        self.assertTrue(partner_buy_rule, "Partner Buy rule is not created")
        self.assertTrue(partner_buy_rule.active, "Partner Buy rule must be active")

        partner_resupply_rule = self.partner_id.partner_resupply_rule_id
        self.assertTrue(partner_resupply_rule, "Partner Resupply rule is not created")
        self.assertTrue(
            partner_resupply_rule.active, "Partner Resupply rule must be active"
        )

    def test_is_subcontractor_partner_switch_off(self):
        self.partner_id.write(
            {
                "is_subcontractor_partner": True,
            }
        )
        self.partner_id.update(
            {
                "is_subcontractor_partner": False,
            }
        )

        location = self.partner_id.subcontracted_created_location_id
        self.assertFalse(location.active, "Location must be not active")

        partner_picking_type = self.partner_id.partner_picking_type_id
        self.assertFalse(partner_picking_type.active, "Picking type must be not active")

        partner_buy_rule = self.partner_id.partner_buy_rule_id
        self.assertFalse(partner_buy_rule.active, "Partner Buy rule must be not active")

        partner_resupply_rule = self.partner_id.partner_resupply_rule_id
        self.assertFalse(
            partner_resupply_rule.active, "Partner Resupply rule must be not active"
        )

    def test_is_subcontractor_partner_switch_on(self):
        self.partner_id.update(
            {
                "is_subcontractor_partner": True,
            }
        )

        location = self.partner_id.subcontracted_created_location_id
        self.assertTrue(location.active, "Location must be active")

        partner_picking_type = self.partner_id.partner_picking_type_id
        self.assertTrue(partner_picking_type.active, "Picking type must be active")

        partner_buy_rule = self.partner_id.partner_buy_rule_id
        self.assertTrue(partner_buy_rule.active, "Partner Buy rule must be active")

        partner_resupply_rule = self.partner_id.partner_resupply_rule_id
        self.assertTrue(
            partner_resupply_rule.active, "Partner Resupply rule must be active"
        )

    def test_is_subcontractor_partner_aсtive_switch_off(self):
        self.partner_id.write(
            {
                "is_subcontractor_partner": True,
            }
        )
        self.partner_id.update(
            {
                "active": False,
            }
        )

        location = self.partner_id.subcontracted_created_location_id
        self.assertFalse(location.active, "Location must be not active")

        partner_picking_type = self.partner_id.partner_picking_type_id
        self.assertFalse(partner_picking_type.active, "Picking type must be not active")

        partner_buy_rule = self.partner_id.partner_buy_rule_id
        self.assertFalse(partner_buy_rule.active, "Partner Buy rule must be not active")

        partner_resupply_rule = self.partner_id.partner_resupply_rule_id
        self.assertFalse(
            partner_resupply_rule.active, "Partner Resupply rule must be not active"
        )

    def test_is_subcontractor_partner_aсtive_switch_on(self):
        self.partner_id.write(
            {
                "is_subcontractor_partner": True,
            }
        )
        self.partner_id.write(
            {
                "active": True,
            }
        )

        location = self.partner_id.subcontracted_created_location_id
        self.assertTrue(location.active, "Location must be active")

        partner_picking_type = self.partner_id.partner_picking_type_id
        self.assertTrue(partner_picking_type.active, "Picking type must be active")

        partner_buy_rule = self.partner_id.partner_buy_rule_id
        self.assertTrue(partner_buy_rule.active, "Partner Buy rule must be active")

        partner_resupply_rule = self.partner_id.partner_resupply_rule_id
        self.assertTrue(
            partner_resupply_rule.active, "Partner Resupply rule must be active"
        )

    def test_is_subcontractor_partner_delete(self):
        partner_id = self.partner_obj.create(
            {
                "name": "Test partner",
                "is_company": True,
                "is_subcontractor_partner": True,
            }
        )

        location = partner_id.subcontracted_created_location_id
        partner_picking_type = partner_id.partner_picking_type_id
        partner_buy_rule = partner_id.partner_buy_rule_id
        partner_resupply_rule = partner_id.partner_resupply_rule_id

        partner_id.unlink()

        self.assertFalse(location.active, "Location must be not active")
        self.assertFalse(partner_picking_type.active, "Picking type must be not active")
        self.assertFalse(partner_buy_rule.active, "Partner Buy rule must be not active")
        self.assertFalse(
            partner_resupply_rule.active, "Partner Resupply rule must be not active"
        )

    def test_check_countof_rules(self):
        partner_id = self.partner_obj.create(
            {
                "name": "Test partner",
                "is_company": True,
                "is_subcontractor_partner": True,
            }
        )
        rules = self.env["stock.rule"].search(
            [("name", "=", partner_id.partner_buy_rule_id.name)]
        )
        self.assertTrue(len(rules) == 2, "There are must be 2 subcontractor rules")

    def test_change_subcontractor_location(self):
        expected_text = "Test partner"
        partner = self.partner_obj.create(
            {
                "name": "Test partner",
                "is_company": True,
                "is_subcontractor_partner": True,
            }
        )
        location = partner.property_stock_subcontractor
        self.assertEqual(
            location.name,
            expected_text,
            msg="Location name must be equal to {}".format(expected_text),
        )

        fields = [
            "subcontracted_created_location_id",
            "partner_buy_rule_id",
            "partner_resupply_rule_id",
            "property_stock_subcontractor",
        ]
        expected_text = "Test partner 1"
        partner.name = expected_text
        for field in fields:
            location = getattr(partner, field)
            self.assertEqual(
                location.name,
                expected_text,
                msg="Record name must be equal to {}".format(expected_text),
            )

        picking = partner.partner_picking_type_id
        expected_text = "%s:  IN" % expected_text
        self.assertEqual(
            picking.name,
            expected_text,
            msg="Record name must be equal to '{}'".format(expected_text),
        )
        self.assertEqual(
            picking.sequence_code, "Tp1I", msg="Sequence code must be equal to 'Tp1I'"
        )

    def test_action_subcontractor_location_stock(self):
        self.partner_id.update({"is_subcontractor_partner": True})
        action = self.partner_id.action_subcontractor_location_stock()
        self.assertEqual(
            action.get("domain"),
            [
                (
                    "location_id",
                    "child_of",
                    self.partner_id.property_stock_subcontractor.ids,
                )
            ],
            msg="Domains must be the same",
        )
        self.assertEqual(
            action.get("res_model"),
            "stock.quant",
            msg="Model must be equal to 'stock.quant'",
        )

    def test_subcontractor_warehouse_rule(self):
        form = Form(
            self.env["res.partner"],
            view="mrp_subcontracting_partner_management.view_partner_form_inherit_subcontractor",  # noqa
        )
        form.name = "Partner Test"
        form.company_type = "company"
        form.subcontractor_resupply_warehouse_ids.add(self.warehouse1)
        with self.assertRaises(exceptions.UserError):
            form.save()
        form.is_subcontractor_partner = True
        partner = form.save()
        self.assertTrue(
            partner.is_subcontractor_partner, msg="Partner must be Subcontractor"
        )
        self.assertEqual(
            len(partner.subcontractor_resupply_warehouse_ids),
            1,
            msg="Partner Warehouses count must be equal to 1",
        )
        self.assertIn(
            self.warehouse1,
            partner.subcontractor_resupply_warehouse_ids,
            msg="Warehouse #1 must be contain in Partner Warehouses",
        )
        self.assertEqual(
            len(partner.partner_resupply_rule_warehouse_ids),
            1,
            msg="Partner Warehouses Rules count must be equal to 1",
        )
        self.assertEqual(
            partner.partner_resupply_rule_warehouse_ids.action,
            "pull",
            msg="Rule action must be equal to 'pull'",
        )
        self.assertEqual(
            partner.partner_resupply_rule_warehouse_ids.partner_address_id.id,
            partner.id,
            msg="Action address id must be equal to {}".format(partner.id),
        )
        self.assertEqual(
            partner.partner_resupply_rule_warehouse_ids.warehouse_id.id,
            self.warehouse1.id,
            msg="Warehouse id must be equal to {}".format(self.warehouse1.id),
        )
        with Form(partner) as form:
            form.subcontractor_resupply_warehouse_ids.add(self.warehouse2)
            form.subcontractor_resupply_warehouse_ids.add(self.warehouse3)

        self.assertEqual(
            len(partner.subcontractor_resupply_warehouse_ids),
            3,
            msg="Partner Warehouses count must be equal to 3",
        )
        self.assertIn(
            self.warehouse2,
            partner.subcontractor_resupply_warehouse_ids,
            msg="Warehouse #2 must be contain in Partner Warehouses",
        )
        self.assertIn(
            self.warehouse3,
            partner.subcontractor_resupply_warehouse_ids,
            msg="Warehouse #3 must be contain in Partner Warehouses",
        )
        self.assertEqual(
            len(partner.partner_resupply_rule_warehouse_ids),
            3,
            msg="Partner Warehouses Rules count must be equal to 3",
        )
        with Form(partner) as form:
            form.subcontractor_resupply_warehouse_ids.remove(id=self.warehouse2.id)
        self.assertEqual(
            len(partner.subcontractor_resupply_warehouse_ids),
            2,
            msg="Partner Warehouses count must be equal to 2",
        )
        self.assertEqual(
            len(partner.partner_resupply_rule_warehouse_ids),
            2,
            msg="Partner Warehouses Rules count must be equal to 2",
        )

        with Form(partner) as form:
            form.is_subcontractor_partner = False
        self.assertEqual(
            len(partner.subcontractor_resupply_warehouse_ids),
            2,
            msg="Partner Warehouses count must be equal to 2",
        )
        self.assertEqual(
            len(partner.partner_resupply_rule_warehouse_ids),
            0,
            msg="Partner Warehouses Rules count must be equal to 0",
        )
        self.assertEqual(
            len(
                partner.with_context(
                    active_test=False
                ).partner_resupply_rule_warehouse_ids
            ),
            3,
            msg="Partner Disable Warehouses Rules count must be equal to 3",
        )
        with Form(partner) as form:
            form.is_subcontractor_partner = True
        self.assertEqual(
            len(
                partner.with_context(
                    active_test=False
                ).partner_resupply_rule_warehouse_ids.filtered(lambda r: not r.active)
            ),
            1,
            msg="Partner Disable Warehouses Rules count must be equal to 1",
        )
        self.assertEqual(
            len(partner.subcontractor_resupply_warehouse_ids),
            2,
            msg="Partner Warehouses count must be equal to 2",
        )
        self.assertEqual(
            len(partner.partner_resupply_rule_warehouse_ids),
            2,
            msg="Partner Warehouses Rules count must be equal to 2",
        )
        partner.write({"active": False})
        self.assertEqual(
            len(partner.subcontractor_resupply_warehouse_ids),
            2,
            msg="Partner Warehouses count must be equal to 2",
        )
        self.assertEqual(
            len(partner.partner_resupply_rule_warehouse_ids),
            0,
            msg="Partner Warehouses Rules count must be equal to 0",
        )
        partner.write({"active": True})
        self.assertEqual(
            len(partner.subcontractor_resupply_warehouse_ids),
            2,
            msg="Partner Warehouses count must be equal to 2",
        )
        self.assertEqual(
            len(partner.partner_resupply_rule_warehouse_ids),
            2,
            msg="Partner Warehouses Rules count must be equal to 2",
        )
