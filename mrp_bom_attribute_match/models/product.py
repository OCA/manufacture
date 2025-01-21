from odoo import _, api, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains("attribute_line_ids")
    def _check_product_with_component_change_allowed(self):
        for template_id in self.filtered("attribute_line_ids"):
            template_attribute_ids = (
                template_id.attribute_line_ids.attribute_id.filtered(
                    lambda tmpl_attr_id: tmpl_attr_id.create_variant != "no_variant"
                )
            )

            for bom_line_id in template_id.bom_ids.bom_line_ids.filtered(
                "match_on_attribute_ids"
            ):
                unmatched_attribute_ids = (
                    bom_line_id.match_on_attribute_ids - template_attribute_ids
                )

                if unmatched_attribute_ids.exists():
                    raise UserError(
                        _(
                            "The attributes you're trying to remove are used in "
                            "the BoM as a match with Component (Product Template). "
                            "To remove these attributes, first remove the BOM line "
                            "with the matching component.\n"
                            "Attributes: %(unmatched_attribute_names)s\nBoM: %(bom_name)s",
                            unmatched_attribute_names=", ".join(
                                unmatched_attribute_ids.mapped("name")
                            ),
                            bom_name=bom_line_id.bom_id.display_name,
                        )
                    )

            for bom_id in (
                self.env["mrp.bom.line"]
                .search([("component_template_id", "=", template_id._origin.id)])
                .bom_id
            ):
                different_attribute_ids = (
                    template_id.attribute_line_ids.attribute_id
                    - bom_id.product_tmpl_id.valid_product_template_attribute_line_ids.attribute_id
                )

                if different_attribute_ids.exists():
                    raise UserError(
                        _(
                            "This product template is used as a component in the "
                            "BOMs for %(bom_name)s and attribute(s) %(different_attribute_names)s are "
                            "not present in all such product(s), and this would "
                            "break the BOM behavior.",
                            bom_name=bom_id.display_name,
                            different_attribute_names=", ".join(
                                different_attribute_ids.mapped("name")
                            ),
                        )
                    )
