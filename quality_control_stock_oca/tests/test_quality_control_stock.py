# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

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
        cls.lot1 = cls.env["stock.lot"].create(
            {
                "name": "Lot for tests-1",
                "product_id": cls.product.id,
            }
        )
        cls.lot2 = cls.env["stock.lot"].create(
            {
                "name": "Lot for tests-2",
                "product_id": cls.product.id,
            }
        )
        cls.product.detailed_type = "product"
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.location.id,
                "quantity": 1,
                "lot_id": cls.lot1.id,
            }
        )
        cls.user = new_test_user(
            cls.env,
            login="test_quality_control_stock_oca",
            groups=f"{'stock.group_stock_user'},{'quality_control_oca.group_quality_control_user'}",
        )
        picking_form = Form(
            cls.env["stock.picking"]
            .with_user(cls.user)
            .with_context(default_picking_type_id=cls.picking_type.id)
        )
        picking_form.partner_id = cls.partner1
        with picking_form.move_ids_without_package.new() as move_form:
            move_form.product_id = cls.product
            move_form.product_uom_qty = 2
        cls.picking1 = picking_form.save()

    def picking_confirmation(self):
        self.picking1.action_confirm()
        self.picking1.move_ids.move_line_ids.quantity = 1

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
        self.picking1.qc_inspections_ids  # noqa: B018
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
        self.picking1.qc_inspections_ids  # noqa: B018
        self.assertEqual(
            self.picking1.created_inspections, 1, "Only one inspection must be created"
        )
        inspection = self.picking1.qc_inspections_ids[:1]
        self.assertEqual(inspection.state, "ready")
        self.assertEqual(inspection.qty, self.picking1.move_ids.quantity)
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
        self.picking1.qc_inspections_ids  # noqa: B018
        self.assertEqual(
            self.picking1.created_inspections, 1, "Only one inspection must be created"
        )
        inspection = self.picking1.qc_inspections_ids[:1]
        self.assertEqual(inspection.state, "plan")
        self.assertEqual(inspection.qty, self.picking1.move_ids.quantity)
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
        self.picking1.qc_inspections_ids  # noqa: B018
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
        self.picking1.qc_inspections_ids  # noqa: B018
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
        self.picking1.qc_inspections_ids  # noqa: B018
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
        self.picking1.qc_inspections_ids  # noqa: B018
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
        self.picking1.qc_inspections_ids  # noqa: B018
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
        self.picking1.qc_inspections_ids  # noqa: B018
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
        self.picking1.qc_inspections_ids  # noqa: B018
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
        self.picking1.qc_inspections_ids  # noqa: B018
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
        self.product.tracking = "lot"
        self.picking1._action_done()
        # pylint: disable=W0104
        self.picking1.qc_inspections_ids  # noqa: B018
        self.assertEqual(
            self.picking1.created_inspections, 1, "Only one inspection must be created"
        )
        self.assertEqual(
            self.picking1.qc_inspections_ids[:1].test,
            self.test,
            "Wrong test picked when creating inspection.",
        )
        self.assertEqual(
            self.lot1.created_inspections, 1, "Only one inspection must be created"
        )
        self.assertEqual(
            self.lot1.qc_inspections_ids[:1].test,
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
        self.assertEqual(
            self.inspection1.product_id, self.picking1.move_ids[:1].product_id
        )
        self.assertEqual(
            self.inspection1.qty, self.picking1.move_ids[:1].product_uom_qty
        )

    def test_qc_inspection_lot_single(self):
        self.trigger.inspection_per_lot = False
        self.product.qc_triggers = [
            (
                0,
                0,
                {"trigger": self.trigger.id, "test": self.test.id, "timing": "after"},
            )
        ]
        self.picking_confirmation()
        self.product.tracking = "lot"
        self.picking1.move_line_ids[0].copy()
        self.picking1.move_line_ids[0].write({"quantity": 1, "lot_id": self.lot1.id})
        self.picking1.move_line_ids[1].write({"quantity": 1, "lot_id": self.lot2.id})
        self.picking1._action_done()
        # pylint: disable=W0104
        self.picking1.qc_inspections_ids  # noqa: B018
        self.assertEqual(
            self.picking1.created_inspections, 1, "One inspections must be created"
        )
        lot1_inspection = self.picking1.qc_inspections_ids.filtered(
            lambda inspection: inspection.lot_id == self.lot1
        )
        self.assertTrue(lot1_inspection, "An inspection with lot1 must be created")
        self.assertEqual(
            lot1_inspection.qty, 2, "Quantity for lot1 must be equal to 2."
        )
        self.assertEqual(
            self.lot1.created_inspections,
            1,
            "Created inspections for lot1 must be equal to 1.",
        )
        lot2_inspection = self.picking1.qc_inspections_ids.filtered(
            lambda inspection: inspection.lot_id == self.lot2
        )
        self.assertFalse(lot2_inspection, "No inspections with lot2 must be created")
        self.assertEqual(
            self.lot2.created_inspections,
            0,
            "Created inspections for lot2 must be equal to 0.",
        )

    def test_qc_inspection_lot_multiple(self):
        self.trigger.inspection_per_lot = True
        self.product.qc_triggers = [
            (
                0,
                0,
                {"trigger": self.trigger.id, "test": self.test.id, "timing": "after"},
            )
        ]
        self.picking_confirmation()
        self.product.tracking = "lot"
        self.picking1.move_line_ids[0].copy()
        self.picking1.move_line_ids[0].write({"quantity": 1, "lot_id": self.lot1.id})
        self.picking1.move_line_ids[1].write({"quantity": 2, "lot_id": self.lot2.id})
        self.picking1._action_done()
        # pylint: disable=W0104
        self.picking1.qc_inspections_ids  # noqa: B018
        self.assertEqual(
            self.picking1.created_inspections, 2, "Two inspections must be created"
        )
        lot1_inspection = self.picking1.qc_inspections_ids.filtered(
            lambda inspection: inspection.lot_id == self.lot1
        )
        self.assertTrue(lot1_inspection, "An inspection with lot1 must be created")
        self.assertEqual(
            lot1_inspection.qty, 1, "Quantity for lot1 must be equal to 1."
        )
        self.assertEqual(
            self.lot1.created_inspections,
            1,
            "Created inspections for lot1 must be equal to 1.",
        )
        lot2_inspection = self.picking1.qc_inspections_ids.filtered(
            lambda inspection: inspection.lot_id == self.lot2
        )
        self.assertTrue(lot2_inspection, "An inspection with lot2 must be created")
        self.assertEqual(
            lot2_inspection.qty, 2, "Quantity for lot1 must be equal to 2."
        )
        self.assertEqual(
            self.lot2.created_inspections,
            1,
            "Created inspections for lot2 must be equal to 1.",
        )
