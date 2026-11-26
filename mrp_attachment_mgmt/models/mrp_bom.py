# Copyright 2022 Tecnativa - Víctor Martínez
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models
from odoo.tools.safe_eval import safe_eval


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    @api.model
    def _get_components_ids(self, products, recursive=False):
        """Gets an objet with the ids of the components, within two arrays:
        'product_template_ids' and 'product_product_ids'.
        Set recursive to get ids of child boms."""
        product_ids = []
        boms_per_product = super()._bom_find(products)
        for bom in boms_per_product.values():
            for bom_line_id in bom.bom_line_ids:
                product_ids.append(bom_line_id.product_id.id)
                if recursive:
                    subcomponents = self._get_components_ids(
                        bom_line_id.product_id,
                        recursive=recursive,
                    )
                    product_ids.extend(subcomponents)
        return product_ids

    def action_see_bom_documents(self):
        product_ids = self._get_components_ids(
            self.product_id or self.product_tmpl_id.product_variant_ids, True
        )
        products = self.env["product.product"].search([("id", "in", product_ids)])
        return products._action_show_attachments()

    def action_show_product_attachments(self):
        if self.product_id:
            return self.product_id._action_show_attachments()
        return self.product_tmpl_id._action_show_attachments()

    def _action_show_attachments(self):
        """Returns the action to show the attachments linked to the bom record."""
        domain = [
            ("res_model", "=", "mrp.bom"),
            ("res_id", "in", self.ids),
        ]
        action = self.env["ir.actions.actions"]._for_xml_id("base.action_attachment")
        context = action.get("context", "{}")
        context = safe_eval(context)
        context["create"] = False
        context["edit"] = False
        action.update({"domain": domain, "context": context})
        return action
