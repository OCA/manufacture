# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_duplicate_with_kit(self):
        self.ensure_one()
        if self.product_variant_count == 1:
            raise models.UserError(
                _("This server action can be used only on products with variants")
            )
        return {
            "name": _("Duplicate with attribute match kit"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "product.template.kit.wizard",
            "context": {
                "default_product_tmpl_id": self.id,
                "default_new_product_template_name": "{} 1".format(self.name),
            },
            "target": "new",
        }
