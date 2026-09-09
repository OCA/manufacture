# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import Form, new_test_user
from odoo.tools import mute_logger

from odoo.addons.quality_control_oca.tests.test_quality_control import (
    TestQualityControlOcaBase,
)


class TestQualityControlStockOca(TestQualityControlOcaBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.qc_trigger_model = cls.env["qc.trigger"]
        cls.picking_type_model = cls.env["stock.picking.type"]
        cls.partner1 = cls.env["res.partner"].create({"name": "Test partner 1"})
        cls.partner2 = cls.env["res.partner"].create({"name": "Test partner 2"})
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.location = cls.picking_type.default_location_src_id
        cls.location_dest = cls.picking_type.default_location_dest_id
        cls.trigger = cls.qc_trigger_model.search(
            [("picking_type_id", "=", cls.picking_type.id)]
        )
        cls.lot = cls.env["stock.lot"].create(
            {
                "name": "Lot for tests",
                "product_id": cls.product.id,
            }
        )
        cls.product.detailed_type = "product"
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.location.id,
                "quantity": 1,
                "lot_id": cls.lot.id,
            }
        )
        cls.user = new_test_user(
            cls.env,
            login="test_quality_control_stock_oca",
            groups="%s,%s"
            % (
                "stock.group_stock_user",
                "quality_control_oca.group_quality_control_user",
            ),
        )
        cls.picking_form = Form(
            cls.env["stock.picking"]
            .with_user(cls.user)
            .with_context(default_picking_type_id=cls.picking_type.id)
        )
        cls.picking_form.partner_id = cls.partner1
        with cls.picking_form.move_ids_without_package.new() as move_form:
            move_form.product_id = cls.product
            move_form.product_uom_qty = 2
        cls.picking1 = cls.picking_form.save()

    def picking_confirmation(self):
        self.picking1.action_confirm()
        self.picking1.move_ids.move_line_ids.qty_done = 1

    @mute_logger("odoo.models.unlink")
    def test_inspection_create_for_product(self):
        self.picking_confirmation()
        self.product.qc_triggers = [
            (
                0,
                0,
                {"trigger": self.trigger.id, "test": self.test.id, "timing": "after"},
            )
        ]
        self.picking1._action_done()
        # Just so _compute_count_inspections() is triggered
        # pylint: disable=W0104
        self.picking1.qc_inspections_ids
        self.assertEqual(
            self.picking1.created_inspections, 1, "Only one inspection must be created"
        )
        inspection = self.picking1.qc_inspections_ids[:1]
        self.assertEqual(inspection.qty, self.picking1.move_ids.product_uom_qty)
        self.assertEqual(
            inspection.test, self.test, "Wrong test picked when creating inspection."
        )
        # Try in this context if onchange with an stock.pack.operation works
        inspection.qty = 5
        inspection.onchange_object_id()
        self.assertEqual(inspection.qty, self.picking1.move_ids.product_uom_qty)

    @mute_logger("odoo.models.unlink")
    def test_inspection_create_for_product_with_before_timing(self):
        self.product.qc_triggers = [
            (
                0,
                0,
                {"trigger": self.trigger.id, "test": self.test.id, "timing": "before"},
            )
        ]
        self.picking_confirmation()
        # Just so _compute_count_inspections() is triggered
        # pylint: disable=W0104
        self.picking1.qc_inspections_ids
        self.assertEqual(
            self.picking1.created_inspections, 1, "Only one inspection must be created"
        )
        inspection = self.picking1.qc_inspections_ids[:1]
        self.assertEqual(inspection.state, "ready")
        self.assertEqual(inspection.qty, self.picking1.move_ids.product_uom_qty)
        self.assertEqual(
            inspection.test, self.test, "Wrong test picked when creating inspection."
        )

    @mute_logger("odoo.models.unlink")
    def test_inspection_create_for_product_with_plan_ahead_timing(self):
        self.product.qc_triggers = [
            (
                0,
                0,
                {
                    "trigger": self.trigger.id,
                    "test": self.test.id,
                    "timing": "plan_ahead",
                },
            )
        ]
        self.picking_confirmation()
        # Just so _compute_count_inspections() is triggered
        # pylint: disable=W0104
        self.picking1.qc_inspections_ids
        self.assertEqual(
            self.picking1.created_inspections, 1, "Only one inspection must be created"
        )
        inspection = self.picking1.qc_inspections_ids[:1]
        self.assertEqual(inspection.state, "plan")
        self.assertEqual(inspection.qty, self.picking1.move_ids.product_uom_qty)
        self.assertEqual(
            inspection.test, self.test, "Wrong test picked when creating inspection."
        )
        self.picking1._action_done()
        self.assertEqual(inspection.state, "ready")

    @mute_logger("odoo.models.unlink")
    def test_inspection_create_for_template(self):
        self.picking_confirmation()
        self.product.product_tmpl_id.qc_triggers = [
            (
                0,
                0,
                {"trigger": self.trigger.id, "test": self.test.id, "timing": "after"},
            )
        ]
        self.picking1._action_done()
        # pylint: disable=W0104
        self.picking1.qc_inspections_ids
        self.assertEqual(
            self.picking1.created_inspections, 1, "Only one inspection must be created"
        )
        self.assertEqual(
            self.picking1.qc_inspections_ids[:1].test,
            self.test,
            "Wrong test picked when creating inspection.",
        )

    @mute_logger("odoo.models.unlink")
    def test_inspection_create_for_category(self):
        self.picking_confirmation()
        self.product.categ_id.qc_triggers = [
            (
                0,
                0,
                {"trigger": self.trigger.id, "test": self.test.id, "timing": "after"},
            )
        ]
        self.picking1._action_done()
        # pylint: disable=W0104
        self.picking1.qc_inspections_ids
        self.assertEqual(
            self.picking1.created_inspections, 1, "Only one inspection must be created"
        )
        self.assertEqual(
            self.picking1.qc_inspections_ids[:1].test,
            self.test,
            "Wrong test picked when creating inspection.",
        )

    @mute_logger("odoo.models.unlink")
    def test_inspection_create_for_product_partner(self):
        self.picking_confirmation()
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
        self.picking1._action_done()
        # pylint: disable=W0104
        self.picking1.qc_inspections_ids
        self.assertEqual(
            self.picking1.created_inspections, 1, "Only one inspection must be created"
        )
        self.assertEqual(
            self.picking1.qc_inspections_ids[:1].test,
            self.test,
            "Wrong test picked when creating inspection.",
        )

    @mute_logger("odoo.models.unlink")
    def test_inspection_create_for_template_partner(self):
        self.picking_confirmation()
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
        self.picking1._action_done()
        # pylint: disable=W0104
        self.picking1.qc_inspections_ids
        self.assertEqual(
            self.picking1.created_inspections, 1, "Only one inspection must be created"
        )
        self.assertEqual(
            self.picking1.qc_inspections_ids[:1].test,
            self.test,
            "Wrong test picked when creating inspection.",
        )

    @mute_logger("odoo.models.unlink")
    def test_inspection_create_for_category_partner(self):
        self.picking_confirmation()
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
        self.picking1._action_done()
        # pylint: disable=W0104
        self.picking1.qc_inspections_ids
        self.assertEqual(
            self.picking1.created_inspections, 1, "Only one inspection must be created"
        )
        self.assertEqual(
            self.picking1.qc_inspections_ids[:1].test,
            self.test,
            "Wrong test picked when creating inspection.",
        )

    @mute_logger("odoo.models.unlink")
    def test_inspection_create_for_product_wrong_partner(self):
        self.picking_confirmation()
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
        self.picking1._action_done()
        # pylint: disable=W0104
        self.picking1.qc_inspections_ids
        self.assertEqual(
            self.picking1.created_inspections, 0, "No inspection must be created"
        )

    @mute_logger("odoo.models.unlink")
    def test_inspection_create_for_template_wrong_partner(self):
        self.picking_confirmation()
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
        self.picking1._action_done()
        # pylint: disable=W0104
        self.picking1.qc_inspections_ids
        self.assertEqual(
            self.picking1.created_inspections, 0, "No inspection must be created"
        )

    @mute_logger("odoo.models.unlink")
    def test_inspection_create_for_category_wrong_partner(self):
        self.picking_confirmation()
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
        self.picking1._action_done()
        # pylint: disable=W0104
        self.picking1.qc_inspections_ids
        self.assertEqual(
            self.picking1.created_inspections, 0, "No inspection must be created"
        )

    @mute_logger("odoo.models.unlink")
    def test_inspection_create_only_one(self):
        self.picking_confirmation()
        self.product.qc_triggers = [
            (0, 0, {"trigger": self.trigger.id, "test": self.test.id})
        ]
        self.product.categ_id.qc_triggers = [
            (0, 0, {"trigger": self.trigger.id, "test": self.test.id})
        ]
        self.picking1._action_done()
        # pylint: disable=W0104
        self.picking1.qc_inspections_ids
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
                "sequence_code": self.picking_type.sequence_code,
                "sequence_id": self.picking_type.sequence_id.id,
            }
        )
        trigger = self.qc_trigger_model.search(
            [("picking_type_id", "=", picking_type.id)]
        )
        self.assertEqual(len(trigger), 1, "One trigger must have been created.")
        self.assertEqual(
            trigger.name,
            picking_type.display_name,
            "Trigger name must match picking type display name.",
        )
        picking_type.write({"name": "Test Name Change"})
        self.assertEqual(
            trigger.name,
            picking_type.display_name,
            "Trigger name must match picking type display name.",
        )

    def test_qc_inspection_picking(self):
        self.inspection1.write(
            {
                "name": self.picking1.move_ids[:1]._name + "inspection",
                "object_id": "%s,%d" % (self.picking1._name, self.picking1.id),
            }
        )
        self.assertEqual(self.inspection1.picking_id, self.picking1)

    def test_qc_inspection_stock_move(self):
        self.picking_confirmation()
        self.inspection1.write(
            {
                "name": self.picking1.move_ids[:1]._name + "inspection",
                "object_id": "%s,%d"
                % (self.picking1.move_ids[:1]._name, self.picking1.move_ids[:1].id),
            }
        )
        self.inspection1.onchange_object_id()
        self.assertEqual(self.inspection1.picking_id, self.picking1)
        self.assertEqual(self.inspection1.lot_id, self.lot)
        self.assertEqual(
            self.inspection1.product_id, self.picking1.move_ids[:1].product_id
        )
        self.assertEqual(
            self.inspection1.qty, self.picking1.move_ids[:1].product_uom_qty
        )

    def test_qc_inspection_lot(self):
        self.inspection1.write(
            {
                "name": self.picking1.move_ids[:1]._name + "inspection",
                "object_id": "%s,%d" % (self.lot._name, self.lot.id),
            }
        )
        self.inspection1.onchange_object_id()
        self.assertEqual(self.inspection1.lot_id, self.lot)
        self.assertEqual(self.inspection1.product_id, self.lot.product_id)

    def test_qc_inspection_mandatory_to_validate(self):
        self.trigger.is_mandatory_to_validate = True
        self.product.qc_triggers = [
            (
                0,
                0,
                {
                    "trigger": self.trigger.id,
                    "test": self.test.id,
                    "timing": "plan_ahead",
                },
            )
        ]
        with self.picking_form.move_ids_without_package.new() as move_form:
            move_form.product_id = self.product
            move_form.product_uom_qty = 2
        picking2 = self.picking_form.save()
        picking2.action_confirm()
        inspection = picking2.qc_inspections_ids
        self.assertTrue(inspection.is_mandatory_to_validate)
        self.assertIn(
            "Control quality is required", picking2.inspection_required_message
        )
        with self.assertRaises(UserError) as m:
            picking2._action_done()
        self.assertIn("inspections before validating", m.exception.args[0])
        self.assertIn(picking2.name, m.exception.args[0])
        # then we confirm the inspection, so we can validate the picking
        for line in inspection.inspection_lines:
            if line.question_type == "qualitative":
                line.qualitative_value = self.val_ok
            if line.question_type == "quantitative":
                line.quantitative_value = 5.0
        inspection.action_confirm()
        picking2._action_done()

    def test_button_validate(self):
        """
        Test behavior of "Validate" button
        to ensure popup appears under certain conditions
        """
        self.inspection1.write(
            {
                "name": self.picking1.move_ids[:1]._name + "inspection",
                "object_id": "%s,%d" % (self.picking1._name, self.picking1.id),
            }
        )

        move1 = self.picking1.move_ids[0]
        move1.quantity_done = 2
        self.product.remind_qc = True

        res = self.picking1.button_validate()
        self.assertNotEqual(res, True)

        self.inspection1.write({"state": "success"})
        res = self.picking1.button_validate()

        self.assertEqual(res, True)
        self.assertEqual(self.picking1.state, "done")

    def test_qc_action_approve(self):
        """
        Test Approve Inspection button when inspection fails
        """
        self.product.auto_scrap = True
        self.picking1.move_ids[0].quantity_done = 2
        self.inspection1.write(
            {
                "name": self.picking1.move_ids[:1]._name + "inspection",
                "object_id": "%s,%d" % (self.picking1._name, self.picking1.id),
                "state": "failed",
                "qty": 2,
            }
        )
        self.inspection1.action_approve()

        self.assertEqual(self.picking1.state, "done")

    def test_no_auto_create_scraps(self):
        """
        Test scraps don't create when inspection fails
        if relative flag is off
        """
        self.picking1.move_ids[0].quantity_done = 2
        self.inspection1.write(
            {
                "name": self.picking1.move_ids[:1]._name + "inspection",
                "object_id": "%s,%d"
                % (self.picking1.move_ids[:1]._name, self.picking1.move_ids[:1].id),
                "state": "failed",
                "qty": 2,
            }
        )
        self.inspection1.onchange_object_id()

        res = self.picking1.button_validate()
        self.assertTrue(res)

        self.assertFalse(self.picking1.has_scrap_move)

    def test_auto_create_scraps(self):
        """
        Test scraps creation when inspection fails
        if relative flag is on
        """
        self.product.auto_scrap = True
        self.picking1.move_ids[:1].quantity_done = 2
        self.inspection1.write(
            {
                "name": self.picking1.move_ids[:1]._name + "inspection",
                "object_id": "%s,%d"
                % (self.picking1.move_ids[:1]._name, self.picking1.move_ids[:1].id),
                "state": "failed",
                "qty": 2,
            }
        )
        self.inspection1.onchange_object_id()

        res = self.picking1.button_validate()
        self.assertTrue(res)

        self.assertTrue(self.picking1.has_scrap_move)

        scraps = self.env["stock.scrap"].search([("picking_id", "=", self.picking1.id)])
        self.assertTrue(all(scrap.state == "done" for scrap in scraps))
