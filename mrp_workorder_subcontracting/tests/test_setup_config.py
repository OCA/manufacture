from odoo.tests import tagged

from .common import WorkorderSubcontractingCommon


@tagged("post_install", "-at_install")
class TestSubcontractingSetupConfig(WorkorderSubcontractingCommon):
    def test_00_plan_fixture_is_self_contained(self):
        """Base test data is created by the suite and avoids demo assumptions."""
        self.assertTrue(self.parts_bom.operation_ids.subcontract_ok)
        self.assertIn(
            self.partner, self.parts_bom.operation_ids.subcontractor_partner_ids
        )
        self.assertEqual(
            self.parts_bom.operation_ids.subcontract_product_id,
            self.service,
        )
        self.assertEqual(
            self.partner.property_stock_subcontract_location_id,
            self.subcontract_location,
        )
        self.assertEqual(
            self.partner.property_stock_virtual_subcontract_location_id,
            self.virtual_subcontract_location,
        )

    def test_01_workorder_gets_subcontract_values_from_operation(self):
        workorder = self._get_workorder(subcontract_parts=True)
        operation = self.parts_bom.operation_ids

        self.assertTrue(workorder.subcontract_ok)
        self.assertEqual(workorder.subcontract_product_id, self.service)
        self.assertEqual(
            workorder.subcontract_partner_ids, operation.subcontractor_partner_ids
        )
        self.assertEqual(workorder.sub_component_move_ids, workorder.move_raw_ids)
        self.assertEqual(workorder.subcontracting_flow, "parts")

    def test_02_finished_flow_workorder_has_no_component_moves(self):
        workorder = self._get_workorder(subcontract_parts=False)

        self.assertTrue(workorder.subcontract_ok)
        self.assertFalse(workorder.move_raw_ids)
        self.assertEqual(workorder.subcontracting_flow, "finished")

    def test_03_wizard_defaults_partner_and_service(self):
        workorder = self._get_workorder(subcontract_parts=True)
        values = (
            self.env["mrp.workorder.assign.subcontract"]
            .with_context(active_ids=workorder.ids)
            .default_get(["partner_ids", "service_id"])
        )

        self.assertEqual(values["service_id"], self.service.id)
        self.assertEqual(
            set(values["partner_ids"][0][2]), set(workorder.subcontract_partner_ids.ids)
        )

    def test_04_purchase_type_configuration_is_complete(self):
        self.assertTrue(self.po_type.is_subcontracting)
        self.assertFalse(self.po_type.immediate_return_subcontracting)
        self.assertEqual(self.po_type.sub_out_picking_type_id, self.parts_out_type)
        self.assertEqual(self.po_type.sub_in_picking_type_id, self.parts_in_type)
        self.assertEqual(
            self.po_type.sub_out_virtual_picking_type_id,
            self.finished_out_type,
        )
        self.assertEqual(
            self.po_type.sub_in_virtual_picking_type_id,
            self.finished_in_type,
        )

    def test_05_warehouse_configuration_is_complete(self):
        self.assertEqual(self.warehouse.sub_out_picking_type_id, self.parts_out_type)
        self.assertEqual(self.warehouse.sub_in_picking_type_id, self.parts_in_type)
        self.assertEqual(
            self.warehouse.sub_out_virtual_picking_type_id,
            self.finished_out_type,
        )
        self.assertEqual(
            self.warehouse.sub_in_virtual_picking_type_id,
            self.finished_in_type,
        )
