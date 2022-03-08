# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import Form, common


class TestMrpAttachmentMgmt(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.component = cls.env["product.product"].create(
            {
                "name": "Test Component A",
                "type": "product",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
            }
        )
        cls.workcenter = cls.env["mrp.workcenter"].create(
            {
                "name": "Test workcenter",
                "resource_calendar_id": cls.env.ref(
                    "resource.resource_calendar_std"
                ).id,
            }
        )
        cls.bom = cls._create_mrp_bom(cls, cls.product, [(cls.component, 1)])
        cls.mrp_production = cls._create_mrp_production(cls)
        cls.workorder = fields.first(cls.mrp_production.workorder_ids)

    def _create_mrp_production(self):
        mrp_production_form = Form(self.env["mrp.production"])
        mrp_production_form.product_id = self.product
        mrp_production_form.bom_id = self.bom
        with mrp_production_form.move_raw_ids.new() as move_form:
            move_form.product_id = self.component
            move_form.product_uom_qty = 1
        mrp_production = mrp_production_form.save()
        mrp_production.action_confirm()
        return mrp_production

    def _create_mrp_bom(self, product, components):
        mrp_bom_form = Form(self.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = product.product_tmpl_id
        for component in components:
            with mrp_bom_form.bom_line_ids.new() as line_form:
                line_form.product_id = component[0]
                line_form.product_qty = component[1]
        with mrp_bom_form.operation_ids.new() as operation_form:
            operation_form.name = "Operation 1"
            operation_form.workcenter_id = self.workcenter
        return mrp_bom_form.save()

    def _create_attachment(self, product):
        return self.env["ir.attachment"].create(
            {
                "name": "Test file %s" % product.name,
                "res_model": product._name,
                "res_id": product.id,
                "datas": base64.b64encode(b"\xff data"),
            }
        )

    def test_misc_bom_documents(self):
        attachment = self._create_attachment(self.component)
        document = self.env["mrp.document"].create({"ir_attachment_id": attachment.id})
        action = self.bom.action_see_bom_documents()
        self.assertIn(
            document.id, self.env["mrp.document"].search(action["domain"]).ids
        )
        action = self.product.action_see_bom_documents()
        self.assertIn(
            document.id, self.env["mrp.document"].search(action["domain"]).ids
        )
        action = self.product.product_tmpl_id.action_see_bom_documents()
        self.assertIn(
            document.id, self.env["mrp.document"].search(action["domain"]).ids
        )

    def test_mrp_workorder_attachments(self):
        with self.assertRaises(UserError):
            self.workorder.action_see_workorder_attachments()
        attachment = self._create_attachment(self.product)
        action = self.workorder.action_see_workorder_attachments()
        self.assertIn(
            attachment.id, self.env["ir.attachment"].search(action["domain"]).ids
        )
