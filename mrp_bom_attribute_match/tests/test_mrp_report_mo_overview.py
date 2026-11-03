from odoo import Command
from odoo.tests import Form

from .common import TestMrpBomAttributeMatchBase


class TestMrpReportMoOverview(TestMrpBomAttributeMatchBase):
    def _create_confirmed_mo(self):
        sword_cyan = self.product_sword.product_variant_ids[0]
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = sword_cyan
        mo_form.bom_id = self.bom_id
        mo_form.product_qty = 1
        mo = mo_form.save()
        mo.action_confirm()
        return mo

    def test_mrp_report_mo_overview(self):
        mo = self._create_confirmed_mo()
        MoOverviewReport = self.env["report.mrp.report_mo_overview"]
        res = MoOverviewReport._get_report_data(mo.id)
        self.assertEqual(res["id"], mo.id)
        self.assertEqual(res["name"], mo.display_name)
        self.assertIn("summary", res)
        self.assertIn("components", res)
        self.assertIn("operations", res)
        self.assertIn("byproducts", res)
        self.assertIn("extras", res)
        self.assertIn("cost_breakdown", res)

    def test_mrp_report_mo_overview_missing_dynamic_component(self):
        # Set a standard_price on the resolved variant so the missing
        # component contributes a measurable cost.
        plastic_cyan = self.product_plastic.product_variant_ids[0]
        plastic_cyan.standard_price = 5.0
        mo = self._create_confirmed_mo()
        dynamic_line = self.bom_id.bom_line_ids.filtered("component_template_id")
        # Detach the dynamic line from its stock move so it shows up in
        # `missing_components` and the override's resolution branch runs.
        mo.move_raw_ids.filtered(lambda m: m.bom_line_id == dynamic_line).write(
            {"bom_line_id": False}
        )
        MoOverviewReport = self.env["report.mrp.report_mo_overview"]
        res = MoOverviewReport._get_report_data(mo.id)
        self.assertEqual(res["id"], mo.id)
        # bom_cost should include the resolved dynamic component (5.0).
        self.assertGreaterEqual(res["summary"]["bom_cost"], 5.0)

    def test_mrp_report_mo_overview_missing_operation(self):
        # Add an operation to the BoM after the MO is confirmed so it appears
        # in `bom_id.operation_ids` but not in `workorder_ids.operation_id`,
        # exercising the `missing_operations` cost roll-up branch.
        workcenter = self.env["mrp.workcenter"].create(
            {
                "name": "Test Workcenter",
                "costs_hour": 60.0,
                "time_efficiency": 100,
                "time_start": 0,
                "time_stop": 0,
            }
        )
        mo = self._create_confirmed_mo()
        bom_cost_before = self.env["report.mrp.report_mo_overview"]._get_report_data(
            mo.id
        )["summary"]["bom_cost"]
        self.bom_id.write(
            {
                "operation_ids": [
                    Command.create(
                        {
                            "name": "Extra Operation",
                            "workcenter_id": workcenter.id,
                            "time_cycle_manual": 60.0,
                            "time_mode": "manual",
                        }
                    )
                ]
            }
        )
        self.assertTrue(
            self.bom_id.operation_ids - mo.workorder_ids.operation_id,
            "Setup should leave at least one missing operation.",
        )
        res = self.env["report.mrp.report_mo_overview"]._get_report_data(mo.id)
        self.assertEqual(res["id"], mo.id)
        # bom_cost should grow by the cost of the newly added operation.
        self.assertGreater(res["summary"]["bom_cost"], bom_cost_before)

    def test_mrp_report_mo_overview_missing_dynamic_component_no_variant(self):
        # Point the dynamic line at a template that shares the Colour
        # attribute but only has a value the produced sword variant does not
        # have, so `_get_component_template_product` returns False and the
        # override hits the `continue` skip branch.
        mo = self._create_confirmed_mo()
        dynamic_line = self.bom_id.bom_line_ids.filtered("component_template_id")
        mo.move_raw_ids.filtered(lambda m: m.bom_line_id == dynamic_line).write(
            {"bom_line_id": False}
        )
        yellow_value = self.env["product.attribute.value"].create(
            {"name": "Yellow", "attribute_id": self.product_attribute.id}
        )
        unmatchable_template = self.env["product.template"].create(
            {
                "name": "Unmatchable Plastic",
                "is_storable": True,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": self.product_attribute.id,
                            "value_ids": [Command.set([yellow_value.id])],
                        }
                    )
                ],
            }
        )
        dynamic_line.component_template_id = unmatchable_template
        MoOverviewReport = self.env["report.mrp.report_mo_overview"]
        res = MoOverviewReport._get_report_data(mo.id)
        self.assertEqual(res["id"], mo.id)
