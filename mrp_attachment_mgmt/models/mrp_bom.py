# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def _action_see_bom_documents_products(self, products):
        domain = [
            "|",
            "&",
            ("ir_attachment_id.res_model", "=", "product.product"),
            ("ir_attachment_id.res_id", "in", products.ids),
            "&",
            ("ir_attachment_id.res_model", "=", "product.template"),
            ("ir_attachment_id.res_id", "in", products.mapped("product_tmpl_id").ids),
        ]
        res = self.env["mrp.bom.line"].action_see_attachments()
        ctx = {"hide_upload": True, "edit": False, "delete": False}
        res.update({"domain": domain, "context": ctx})
        return res

    @api.model
    def _get_components_ids(self, product_tmpl=None, product=None, recursive=False):
        """Gets an objet with the ids of the components, within two arrays:
        'product_template_ids' and 'product_product_ids'.
        Set recursive to get ids of child boms."""
        product_ids = []
        bom = super()._bom_find(product_tmpl=product_tmpl, product=product)
        for bom_line_id in bom.bom_line_ids:
            product_ids.append(bom_line_id.product_id.id)
            if recursive:
                subcomponents = self._get_components_ids(
                    product_tmpl=bom_line_id.product_id.product_tmpl_id,
                    product=bom_line_id.product_id,
                    recursive=recursive,
                )
                product_ids.extend(subcomponents)
        return product_ids

    def _action_see_bom_documents(self, product_tmpl=None, product=None):
        product_ids = self._get_components_ids(product_tmpl, product, True)
        products = self.env["product.product"].search([("id", "in", product_ids)])
        return self._action_see_bom_documents_products(products)

    def action_see_bom_documents(self):
        return self._action_see_bom_documents(
            product_tmpl=self.product_tmpl_id, product=self.product_id
        )
