# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields
from odoo.tests.common import Form, TransactionCase


class TestMrpProductionInjectOperation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product_template_drawer = cls.env.ref(
            "product.product_product_27_product_template"
        )
        cls.product_drawer = cls.env.ref("product.product_product_27")
        cls.bom_drawer = cls.env.ref("mrp.mrp_bom_drawer_rout")
        cls.packing_operation = cls.env.ref("mrp.mrp_routing_workcenter_4")
        cls.testing_operation = cls.env.ref("mrp.mrp_routing_workcenter_3")
        cls.assembly_operation = cls.env.ref("mrp.mrp_routing_workcenter_1")
        cls.assembly_line_workcenter = cls.env.ref("mrp.mrp_workcenter_3")
        cls.productive_time = cls.env.ref("mrp.block_reason7")

        cls.color_attribute = cls.env.ref("product.product_attribute_2")
        cls.color_att_value_white = cls.env.ref("product.product_attribute_value_3")
        cls.color_att_value_black = cls.env.ref("product.product_attribute_value_4")

    @classmethod
    def _define_color_attribute_on_drawer(cls):
        """
        Redefine Drawer product to manage attributes by:
        - Creating white product
        - Defining color as attribute of drawer product with white and black values
        - Adding white component to the BOM drawer applying only on selected variant
        - Adding a painting operation to the BOM drawer consuming white product only
         on selected variant

        """
        white_color_product_tmpl_form = Form(cls.env["product.template"])
        white_color_product_tmpl_form.name = "White color"
        white_color_product_tmpl = white_color_product_tmpl_form.save()

        cls.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": cls.product_template_drawer.id,
                "attribute_id": cls.color_attribute.id,
                "value_ids": [
                    fields.Command.set(
                        [cls.color_att_value_white.id, cls.color_att_value_black.id]
                    )
                ],
            }
        )

        tmpl_attr_value_white = cls.env["product.template.attribute.value"].search(
            [
                ("product_tmpl_id", "=", cls.product_template_drawer.id),
                ("product_attribute_value_id", "=", cls.color_att_value_white.id),
            ]
        )
        tmpl_attr_value_black = cls.env["product.template.attribute.value"].search(
            [
                ("product_tmpl_id", "=", cls.product_template_drawer.id),
                ("product_attribute_value_id", "=", cls.color_att_value_black.id),
            ]
        )

        cls.env["mrp.bom.line"].create(
            {
                "bom_id": cls.bom_drawer.id,
                "product_id": white_color_product_tmpl.product_variant_id.id,
                "bom_product_template_attribute_value_ids": [
                    fields.Command.link(tmpl_attr_value_white.id)
                ],
            }
        )

        cls.env["mrp.routing.workcenter"].create(
            {
                "name": "Painting",
                "bom_id": cls.bom_drawer.id,
                "workcenter_id": cls.assembly_line_workcenter.id,
                "bom_product_template_attribute_value_ids": [
                    fields.Command.link(tmpl_attr_value_white.id)
                ],
            }
        )

        white_drawer = cls.product_template_drawer.product_variant_ids.filtered(
            lambda p: p.product_template_variant_value_ids == tmpl_attr_value_white
        )
        black_drawer = cls.product_template_drawer.product_variant_ids.filtered(
            lambda p: p.product_template_variant_value_ids == tmpl_attr_value_black
        )

        return white_drawer, black_drawer

    @classmethod
    def _create_manufacturing_order(cls, product, bom=None):
        mo_form = Form(cls.env["mrp.production"])
        mo_form.product_id = product
        if bom is not None:
            mo_form.bom_id = bom
        mo = mo_form.save()
        return mo

    @classmethod
    def _get_injector_wizard_form(cls, production):
        action = production.action_open_workorder_injector()
        injector_form = Form(
            cls.env[action["res_model"]].with_context(**action.get("context", {}))
        )
        return injector_form

    @classmethod
    def _inject_operation(cls, production, new_operation, previous_workorder):
        injector_form = cls._get_injector_wizard_form(production)
        injector_form.operation_id = new_operation
        injector_form.workorder_id = previous_workorder
        injector_wiz = injector_form.save()
        injector_wiz.action_add_operation()

    @classmethod
    def _get_new_workorder(cls, previously_existing_wos, existing_wos):
        return previously_existing_wos - existing_wos

    @classmethod
    def _record_time_tracking(cls, workorder, duration, productivity):
        workorder_form = Form(workorder)
        with workorder_form.time_ids.new() as time_tracking_form:
            time_tracking_form.date_end = fields.Datetime.add(
                time_tracking_form.date_start, seconds=duration
            )
            time_tracking_form.loss_id = productivity

    def test_injector_allowed_operations_no_variant(self):
        """Test only operations from bom are allowed in wizard"""
        mo = self._create_manufacturing_order(self.product_drawer, self.bom_drawer)
        mo.action_confirm()
        injector_form = self._get_injector_wizard_form(mo)
        non_related_bom_operations = self.env["mrp.routing.workcenter"].search(
            [("id", "not in", self.bom_drawer.operation_ids.ids)]
        )
        self.assertTrue(non_related_bom_operations)
        for op in non_related_bom_operations:
            self.assertNotIn(op, injector_form.allowed_bom_operation_ids)
        for op in mo.bom_id.operation_ids:
            self.assertIn(op, injector_form.allowed_bom_operation_ids)

    def test_injector_allowed_operations_variant(self):
        """Test only operations from bom are allowed in wizard"""
        white_drawer, black_drawer = self._define_color_attribute_on_drawer()
        mo = self._create_manufacturing_order(white_drawer, self.bom_drawer)
        mo.action_confirm()
        injector_form = self._get_injector_wizard_form(mo)
        for op in mo.bom_id.operation_ids:
            self.assertIn(op, injector_form.allowed_bom_operation_ids)
        mo = self._create_manufacturing_order(black_drawer, self.bom_drawer)
        mo.action_confirm()
        injector_form = self._get_injector_wizard_form(mo)
        for op in mo.bom_id.operation_ids:
            if op.bom_product_template_attribute_value_ids:
                self.assertEqual(op.name, "Painting")
                self.assertNotIn(op, injector_form.allowed_bom_operation_ids)
            else:
                self.assertIn(op, injector_form.allowed_bom_operation_ids)

    def test_injector_allowed_workorders_no_variant(self):
        """Test only workorders from manufacturing order are allowed in wizard"""
        mo = self._create_manufacturing_order(self.product_drawer, self.bom_drawer)
        mo.action_confirm()
        injector_form = self._get_injector_wizard_form(mo)
        non_mo_workorders = self.env["mrp.workorder"].search(
            [("id", "not in", mo.workorder_ids.ids)]
        )
        for wo in non_mo_workorders:
            self.assertNotIn(wo, injector_form.production_workorder_ids)
        for wo in mo.workorder_ids:
            self.assertIn(wo, injector_form.production_workorder_ids)
        # Ensure only last done workorder is selectable as previous operation
        first_workorder = fields.first(mo.workorder_ids)
        second_workorder = first_workorder.next_work_order_id
        third_workorder = second_workorder.next_work_order_id
        first_workorder.button_start()
        first_workorder.button_finish()
        second_workorder.button_start()
        second_workorder.button_finish()
        injector_form = self._get_injector_wizard_form(mo)
        self.assertNotIn(first_workorder, injector_form.production_workorder_ids)
        self.assertIn(second_workorder, injector_form.production_workorder_ids)
        self.assertIn(third_workorder, injector_form.production_workorder_ids)

    def test_inject_operation(self):
        mo = self._create_manufacturing_order(self.product_drawer, self.bom_drawer)
        mo.action_confirm()
        mo.button_plan()
        first_workorder = fields.first(mo.workorder_ids)
        second_workorder = first_workorder.next_work_order_id
        third_workorder = second_workorder.next_work_order_id
        # Inject extra testing operation at the end
        self._inject_operation(mo, self.testing_operation, third_workorder)
        self.assertEqual(len(mo.workorder_ids), 4)
        last_workorder = fields.first(mo.workorder_ids.sorted(reverse=True))
        self.assertEqual(last_workorder.name, self.testing_operation.name)
        self.assertEqual(last_workorder.operation_id, self.testing_operation)
        self.assertEqual(
            last_workorder.workcenter_id, self.testing_operation.workcenter_id
        )
        self.assertEqual(last_workorder.state, "pending")
        self.assertEqual(last_workorder.sequence, 4)
        self.assertEqual(
            last_workorder.date_planned_start, third_workorder.date_planned_finished
        )
        self.assertEqual(
            last_workorder.date_planned_finished,
            last_workorder.workcenter_id.resource_calendar_id.plan_hours(
                last_workorder.duration_expected / 60.0,
                last_workorder.date_planned_start,
                compute_leaves=True,
                domain=[("time_type", "in", ["leave", "other"])],
            ),
        )
        self.assertEqual(third_workorder.next_work_order_id, last_workorder)
        # Start first op and register time tracking
        first_workorder.button_start()
        self._record_time_tracking(first_workorder, 60, self.productive_time)
        first_workorder.button_finish()
        self.assertEqual(first_workorder.state, "done")
        self.assertEqual(second_workorder.state, "ready")
        # Inject extra packing operation before second workorder
        pre_existing_wo_ids = set(mo.workorder_ids.ids)
        self._inject_operation(mo, self.packing_operation, first_workorder)
        existing_wo_ids = set(mo.workorder_ids.ids)
        new_workorder = self.env["mrp.workorder"].browse(
            existing_wo_ids - pre_existing_wo_ids
        )
        self.assertEqual(new_workorder.state, "ready")
        self.assertEqual(new_workorder.sequence, 2)
        self.assertEqual(
            new_workorder.date_planned_start,
            new_workorder.workcenter_id.resource_calendar_id.plan_hours(
                -new_workorder.duration_expected / 60.0,
                new_workorder.date_planned_finished,
                compute_leaves=True,
                domain=[("time_type", "in", ["leave", "other"])],
            ),
        )
        self.assertEqual(
            new_workorder.date_planned_finished, second_workorder.date_planned_start
        )
        self.assertEqual(new_workorder.next_work_order_id, second_workorder)
        # Second workorder is now the third one
        self.assertEqual(second_workorder.state, "pending")
        self.assertEqual(second_workorder.sequence, 3)
        self.assertEqual(second_workorder.next_work_order_id, third_workorder)
        # Third workorder is now the fourth one
        self.assertEqual(third_workorder.state, "pending")
        self.assertEqual(third_workorder.sequence, 4)
        self.assertEqual(third_workorder.next_work_order_id, last_workorder)
        # Last workorder is still the last one
        self.assertEqual(last_workorder.state, "pending")
        self.assertEqual(last_workorder.sequence, 5)
        self.assertFalse(last_workorder.next_work_order_id)
