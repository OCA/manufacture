from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import WorkorderSubcontractingCommon


@tagged("post_install", "-at_install")
class TestSubcontractingPermissionsValidations(WorkorderSubcontractingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mrp_manager_no_flow_user = cls.env["res.users"].create(
            {
                "name": "MRP Manager Without Subcontract Flow Groups",
                "login": "mrp_manager_no_subcontract_flow_groups",
                "email": "mrp_manager_no_flow@example.com",
                "groups_id": [
                    Command.set(
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("mrp.group_mrp_manager").id,
                        ]
                    )
                ],
            }
        )

    def test_01_user_without_urgent_group_cannot_select_urgent_flow(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        wizard_model = self.env["mrp.workorder.assign.subcontract"].with_user(
            self.mrp_manager_no_flow_user
        )

        with self.assertRaises(ValidationError):
            wizard_model.create(
                {
                    "workorder_ids": [Command.set(workorder.ids)],
                    "partner_ids": [Command.set(self.partner.ids)],
                    "date_finished": self.fixed_date,
                    "flow_type": "urgent",
                    "urgent_note": "Not allowed for this user",
                    "service_id": self.service.id,
                }
            )

    def test_02_user_without_subcontractor_stock_group_cannot_select_flow(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        wizard_model = self.env["mrp.workorder.assign.subcontract"].with_user(
            self.mrp_manager_no_flow_user
        )

        with self.assertRaises(ValidationError):
            wizard_model.create(
                {
                    "workorder_ids": [Command.set(workorder.ids)],
                    "partner_ids": [Command.set(self.partner.ids)],
                    "date_finished": self.fixed_date,
                    "flow_type": "subcontractor_stock",
                    "service_id": self.service.id,
                }
            )

    def test_03_urgent_flow_requires_reason(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        wizard = self._create_stock_wizard(workorder, "urgent")

        with self.assertRaises(ValidationError):
            wizard.assign()

    def test_04_selected_supplier_must_be_allowed_on_workorder(self):
        workorder = self._get_workorder(subcontract_parts=True, qty=10.0)
        invalid_partner = self.env["res.partner"].create(
            {
                "name": "Invalid Subcontractor",
                "property_stock_subcontract_location_id": self.subcontract_location.id,
                "property_stock_virtual_subcontract_location_id": (
                    self.virtual_subcontract_location.id
                ),
            }
        )
        wizard = self._create_stock_wizard(
            workorder,
            "urgent",
            partner=invalid_partner,
            urgent_note="Supplier is not allowed",
        )

        with self.assertRaises(ValidationError):
            wizard.assign()
