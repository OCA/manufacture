from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestSubcontractedPartner(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_id = cls.env.ref("base.res_partner_12")
        cls.partner_obj = cls.env["res.partner"]

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
