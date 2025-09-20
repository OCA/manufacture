# Copyright 2022 Tecnativa - Víctor Martínez
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models


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
        context = {
            "default_res_model": "product.template",
            "default_res_id": len(self.ids) == 1 and self.id or None,
            "default_company_id": self.company_id.id,
        }
        return {
            "name": _("Attachments"),
            "domain": domain,
            "res_model": "product.document",
            "type": "ir.actions.act_window",
            "view_mode": "kanban,list,form",
            "target": "current",
            "context": context,
            "search_view_id": self.env.ref("product.product_document_search").ids,
        }


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
        context = {
            "default_res_model": "product.product",
            "default_res_id": len(self.ids) == 1 and self.id or None,
            "default_company_id": self.company_id.id,
        }
        return {
            "name": _("Attachments"),
            "domain": domain,
            "res_model": "product.document",
            "type": "ir.actions.act_window",
            "view_mode": "kanban,list,form",
            "target": "current",
            "context": context,
            "search_view_id": self.env.ref("product.product_document_search").ids,
        }
