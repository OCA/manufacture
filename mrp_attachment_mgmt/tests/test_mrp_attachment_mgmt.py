# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError

from .common import TestMrpAttachmentMgmtBase


class TestMrpAttachmentMgmt(TestMrpAttachmentMgmtBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_misc_bom_documents(self):
        attachment_a = self._create_attachment(self.component_a)
        self.env["mrp.document"].create({"ir_attachment_id": attachment_a.id})
        attachment_b = self._create_attachment(self.component_b)
        action = self.bom.action_see_bom_documents()
        attachment_bom_items = self.attachment_model.search(action["domain"])
        self.assertEqual(len(attachment_bom_items), 2)
        self.assertIn(attachment_a.id, attachment_bom_items.ids)
        self.assertIn(attachment_b.id, attachment_bom_items.ids)
        self.assertNotIn(self.component_c.id, attachment_bom_items.mapped("res_id"))
        action = self.product.action_see_bom_documents()
        attachment_product_items = self.attachment_model.search(action["domain"])
        self.assertEqual(attachment_bom_items, attachment_product_items)
        action = self.product.product_tmpl_id.action_see_bom_documents()
        attachment_template_items = self.attachment_model.search(action["domain"])
        self.assertEqual(attachment_template_items, attachment_product_items)

    def test_mrp_workorder_attachments(self):
        with self.assertRaises(UserError):
            self.workorder.action_see_workorder_attachments()
        attachment = self._create_attachment(self.product)
        action = self.workorder.action_see_workorder_attachments()
        self.assertIn(attachment.id, self.attachment_model.search(action["domain"]).ids)
