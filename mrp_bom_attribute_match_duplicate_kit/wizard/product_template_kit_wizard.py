# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class ProductTemplateKitWizard(models.TransientModel):
    _name = "product.template.kit.wizard"
    _description = "Duplicate with attribute match kit"

    product_tmpl_id = fields.Many2one(comodel_name="product.template", required=True)
    new_product_template_name = fields.Char(required=True)

    def action_confirm(self):
        """Duplicate product with bom"""
        if self.product_tmpl_id.name == self.new_product_template_name:
            raise models.UserError(
                _("The name of the new product template should not be the same name")
            )
        new_product = self.product_tmpl_id.copy(
            default={"name": self.new_product_template_name}
        )
        self.env["mrp.bom"].create(
            {
                "product_tmpl_id": new_product.id,
                "type": "phantom",
                "product_qty": 1,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "component_template_id": self.product_tmpl_id.id,
                            "match_on_attribute_ids": [
                                (
                                    6,
                                    0,
                                    self.product_tmpl_id.attribute_line_ids.mapped(
                                        "attribute_id"
                                    ).ids,
                                )
                            ],
                            "product_uom_id": self.product_tmpl_id.uom_id.id,
                        },
                    )
                ],
            }
        )
        return {
            "type": "ir.actions.act_window",
            "name": self.new_product_template_name,
            "view_mode": "form",
            "res_model": "product.template",
            "res_id": new_product.id,
        }
