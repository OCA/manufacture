# Copyright 2022 Tecnativa - Víctor Martínez
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_see_bom_documents(self):
        return fields.first(self.bom_ids).action_see_bom_documents()

    def action_see_bom_attachments(self):
        return self.bom_ids._action_show_attachments()

    def _action_show_attachments(self):
        """Returns the action to show the attachments linked to the products
        recordset or to their templates.
        """
        domain = [
            ("res_model", "=", "product.template"),
            ("res_id", "in", self.ids),
        ]
        action = self.env["ir.actions.actions"]._for_xml_id("base.action_attachment")
        action.update({"domain": domain})
        return action


class ProductProduct(models.Model):
    _inherit = "product.product"

    def action_see_bom_documents(self):
        return fields.first(self.bom_ids).action_see_bom_documents()

    def action_see_bom_attachments(self):
        return self.bom_ids._action_show_attachments()

    def _action_show_attachments(self):
        """Returns the action to show the attachments linked to the products
        recordset or to their templates.
        """
        domain = [
            "|",
            "&",
            ("res_model", "=", "product.product"),
            ("res_id", "in", self.ids),
            "&",
            ("res_model", "=", "product.template"),
            ("res_id", "in", self.product_tmpl_id.ids),
        ]
        action = self.env["ir.actions.actions"]._for_xml_id("base.action_attachment")
        action.update({"domain": domain})
        return action
