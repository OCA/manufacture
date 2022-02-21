# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestQualityControl(TransactionCase):
    def setUp(self):
        super().setUp()
        self.users_model = self.env["res.users"]
        self.picking_model = self.env["stock.picking"]
        self.inspection_model = self.env["qc.inspection"]
        self.qc_trigger_model = self.env["qc.trigger"]
        self.picking_type_model = self.env["stock.picking.type"]
        self.product = self.env.ref("product.product_product_2")
        self.partner1 = self.env.ref("base.res_partner_2")
        self.partner2 = self.env.ref("base.res_partner_4")
        self.test = self.env.ref("quality_control_oca.qc_test_1")
        self.picking_type = self.env.ref("stock.picking_type_out")
        self.location_dest = self.env.ref("stock.stock_location_customers")
        self.group_stock_user = self.env.ref("stock.group_stock_user")
        self.group_quality_control_user = self.env.ref(
            "quality_control_oca.group_quality_control_user"
        )
        self.company = self.env.ref("base.main_company")
        self.sequence = self.env["ir.sequence"].create(
            {"code": "out", "name": "outgoing_sequence"}
        )
        inspection_lines = self.inspection_model._prepare_inspection_lines(self.test)
        self.inspection1 = self.inspection_model.create(
            {"name": "Test Inspection", "inspection_lines": inspection_lines}
        )
        self.trigger = self.qc_trigger_model.search(
            [("picking_type_id", "=", self.picking_type.id)]
        )
        self.lot = self.env["stock.production.lot"].create(
            {
                "name": "Lot for tests",
                "product_id": self.product.id,
                "company_id": self.company.id,
            }
        )
        self.user1_id = self._create_user(
            "user_1",
            [self.group_stock_user, self.group_quality_control_user],
            self.company,
        )
        move_vals = {
            "name": self.product.name,
            "product_id": self.product.id,
            "product_uom": self.product.uom_id.id,
            "product_uom_qty": 2.0,
            "location_id": self.picking_type.default_location_src_id.id,
            "location_dest_id": self.location_dest.id,
            "quantity_done": 1.0,
        }
        self.picking1 = (
            self.picking_model.with_user(self.user1_id)
            .with_context(default_picking_type_id=self.picking_type.id)
            .create(
                {
                    "partner_id": self.partner1.id,
                    "picking_type_id": self.picking_type.id,
                    "move_lines": [(0, 0, move_vals)],
                    "location_dest_id": self.location_dest.id,
                }
            )
        )
        self.picking1.action_confirm()
        sequence = 10
        for line in self.picking1.move_lines.filtered(
            lambda r: r.product_id == self.product
        ):
            line.write(
                {
                    "move_line_ids": [
                        (
                            0,
                            0,
                            {
                                "lot_id": self.lot.id,
                                "product_uom_qty": 1.0,
                                "qty_done": 1.0,
                                "product_uom_id": line.product_uom.id,
                                "product_id": line.product_id.id,
                                "location_id": line.location_id.id,
                                "location_dest_id": line.location_dest_id.id,
                            },
                        )
                    ],
                    "sequence": sequence,
                }
            )
            sequence += 10

    def _create_user(self, login, groups, company):
        """ Create a user."""
        group_ids = [group.id for group in groups]
        user = self.users_model.with_context({"no_reset_password": True}).create(
            {
                "name": "Sale User",
                "login": login,
                "password": "test",
                "email": "test@yourcompany.com",
                "company_id": company.id,
                "company_ids": [(4, company.id)],
                "groups_id": [(6, 0, group_ids)],
            }
        )
        return user.id

    def test_inspection_create_for_product(self):
        self.product.qc_triggers = [
            (0, 0, {"trigger": self.trigger.id, "test": self.test.id})
        ]
        self.picking1.button_validate()
        self.assertEqual(
            self.picking1.created_inspections, 1, "Only one inspection must be created"
        )
        inspection = self.picking1.qc_inspections_ids[:1]
        self.assertEqual(inspection.qty, 2.0)
        self.assertEqual(
            inspection.test, self.test, "Wrong test picked when creating inspection."
        )
        # Try in this context if onchange with an stock.pack.operation works
        inspection.qty = 5
        inspection.onchange_object_id()
        self.assertEqual(inspection.qty, 2.0)

    def test_inspection_create_for_template(self):
        self.product.product_tmpl_id.qc_triggers = [
            (0, 0, {"trigger": self.trigger.id, "test": self.test.id})
        ]
        self.picking1.button_validate()
        self.assertEqual(
            self.picking1.created_inspections, 1, "Only one inspection must be created"
        )
        self.assertEqual(
            self.picking1.qc_inspections_ids[:1].test,
            self.test,
            "Wrong test picked when creating inspection.",
        )

    def test_inspection_create_for_category(self):
        self.product.categ_id.qc_triggers = [
            (0, 0, {"trigger": self.trigger.id, "test": self.test.id})
        ]
        self.picking1.button_validate()
        self.assertEqual(
            self.picking1.created_inspections, 1, "Only one inspection must be created"
        )
        self.assertEqual(
            self.picking1.qc_inspections_ids[:1].test,
            self.test,
            "Wrong test picked when creating inspection.",
        )

    def test_inspection_create_for_product_partner(self):
        self.product.qc_triggers = [
            (
                0,
                0,
                {
                    "trigger": self.trigger.id,
                    "test": self.test.id,
                    "partners": [(6, 0, self.partner1.ids)],
                },
            )
        ]
        self.picking1.button_validate()
        self.assertEqual(
            self.picking1.created_inspections, 1, "Only one inspection must be created"
        )
        self.assertEqual(
            self.picking1.qc_inspections_ids[:1].test,
            self.test,
            "Wrong test picked when creating inspection.",
        )

    def test_inspection_create_for_template_partner(self):
        self.product.product_tmpl_id.qc_triggers = [
            (
                0,
                0,
                {
                    "trigger": self.trigger.id,
                    "test": self.test.id,
                    "partners": [(6, 0, self.partner1.ids)],
                },
            )
        ]
        self.picking1.button_validate()
        self.assertEqual(
            self.picking1.created_inspections, 1, "Only one inspection must be created"
        )
        self.assertEqual(
            self.picking1.qc_inspections_ids[:1].test,
            self.test,
            "Wrong test picked when creating inspection.",
        )

    def test_inspection_create_for_category_partner(self):
        self.product.categ_id.qc_triggers = [
            (
                0,
                0,
                {
                    "trigger": self.trigger.id,
                    "test": self.test.id,
                    "partners": [(6, 0, self.partner1.ids)],
                },
            )
        ]
        self.picking1.button_validate()
        self.assertEqual(
            self.picking1.created_inspections, 1, "Only one inspection must be created"
        )
        self.assertEqual(
            self.picking1.qc_inspections_ids[:1].test,
            self.test,
            "Wrong test picked when creating inspection.",
        )

    def test_inspection_create_for_product_wrong_partner(self):
        self.product.qc_triggers = [
            (
                0,
                0,
                {
                    "trigger": self.trigger.id,
                    "test": self.test.id,
                    "partners": [(6, 0, self.partner2.ids)],
                },
            )
        ]
        self.picking1.button_validate()
        self.assertEqual(
            self.picking1.created_inspections, 0, "No inspection must be created"
        )

    def test_inspection_create_for_template_wrong_partner(self):
        self.product.product_tmpl_id.qc_triggers = [
            (
                0,
                0,
                {
                    "trigger": self.trigger.id,
                    "test": self.test.id,
                    "partners": [(6, 0, self.partner2.ids)],
                },
            )
        ]
        self.picking1.button_validate()
        self.assertEqual(
            self.picking1.created_inspections, 0, "No inspection must be created"
        )

    def test_inspection_create_for_category_wrong_partner(self):
        self.product.categ_id.qc_triggers = [
            (
                0,
                0,
                {
                    "trigger": self.trigger.id,
                    "test": self.test.id,
                    "partners": [(6, 0, self.partner2.ids)],
                },
            )
        ]
        self.picking1.button_validate()
        self.assertEqual(
            self.picking1.created_inspections, 0, "No inspection must be created"
        )

    def test_inspection_create_only_one(self):
        self.product.qc_triggers = [
            (0, 0, {"trigger": self.trigger.id, "test": self.test.id})
        ]
        self.product.categ_id.qc_triggers = [
            (0, 0, {"trigger": self.trigger.id, "test": self.test.id})
        ]
        self.picking1.button_validate()
        self.assertEqual(
            self.picking1.created_inspections, 1, "Only one inspection must be created"
        )
        self.assertEqual(
            self.picking1.qc_inspections_ids[:1].test,
            self.test,
            "Wrong test picked when creating inspection.",
        )
        self.assertEqual(
            self.lot.created_inspections, 1, "Only one inspection must be created"
        )
        self.assertEqual(
            self.lot.qc_inspections_ids[:1].test,
            self.test,
            "Wrong test picked when creating inspection.",
        )

    def test_picking_type(self):
        picking_type = self.picking_type_model.create(
            {
                "name": "Test Picking Type",
                "code": "outgoing",
                "sequence_code": "OUT",
                "sequence_id": self.sequence.id,
            }
        )
        trigger = self.qc_trigger_model.search(
            [("picking_type_id", "=", picking_type.id)]
        )
        self.assertEqual(len(trigger), 1, "One trigger must have been created.")
        self.assertEqual(
            trigger.name,
            picking_type.name,
            "Trigger name must match picking type name.",
        )
        picking_type.write({"name": "Test Name Change"})
        self.assertEqual(
            trigger.name,
            picking_type.name,
            "Trigger name must match picking type name.",
        )

    def test_qc_inspection_picking(self):
        self.inspection1.write(
            {
                "name": self.picking1.move_lines[:1]._name + "inspection",
                "object_id": "%s,%d" % (self.picking1._name, self.picking1.id),
            }
        )
        self.assertEqual(self.inspection1.picking_id, self.picking1)

    def test_qc_inspection_stock_move(self):
        self.inspection1.write(
            {
                "name": self.picking1.move_lines[:1]._name + "inspection",
                "object_id": "%s,%d"
                % (self.picking1.move_lines[:1]._name, self.picking1.move_lines[:1].id),
            }
        )
        self.inspection1.onchange_object_id()
        self.assertEqual(self.inspection1.picking_id, self.picking1)
        self.assertEqual(self.inspection1.lot_id, self.lot)
        self.assertEqual(
            self.inspection1.product_id, self.picking1.move_lines[:1].product_id
        )
        self.assertEqual(self.inspection1.qty, self.picking1.move_lines[:1].product_qty)

    def test_qc_inspection_lot(self):
        self.inspection1.write(
            {
                "name": self.picking1.move_lines[:1]._name + "inspection",
                "object_id": "%s,%d" % (self.lot._name, self.lot.id),
            }
        )
        self.inspection1.onchange_object_id()
        self.assertEqual(self.inspection1.lot_id, self.lot)
        self.assertEqual(self.inspection1.product_id, self.lot.product_id)
