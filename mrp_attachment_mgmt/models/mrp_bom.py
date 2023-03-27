# Copyright 2022 Tecnativa - Víctor Martínez
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

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

    def action_see_bom_documents(self):
        product_ids = self._get_components_ids(
            self.product_tmpl_id, self.product_id, True
        )
        products = self.env["product.product"].search([("id", "in", product_ids)])
        return products._action_show_attachments()
