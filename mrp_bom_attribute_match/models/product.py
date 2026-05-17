from odoo import _, api, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains("attribute_line_ids")
    def _check_product_with_component_change_allowed(self):
        for template in self.filtered("attribute_line_ids"):
            template_attrs = template.attribute_line_ids.attribute_id.filtered(
                lambda a: a.create_variant != "no_variant"
            )

            for bom_line in template.bom_ids.bom_line_ids.filtered(
                "match_on_attribute_ids"
            ):
                missing = bom_line.match_on_attribute_ids - template_attrs
                if missing:
                    raise UserError(
                        _(
                            "The attributes you're trying to remove are used in "
                            "the BoM as a match with Component (Product Template). "
                            "To remove these attributes, first remove the BoM line "
                            "with the matching component.\n"
                            "Attributes: %(attributes)s\nBoM: %(bom)s",
                            attributes=", ".join(missing.mapped("name")),
                            bom=bom_line.bom_id.display_name,
                        )
                    )

            using_boms = (
                self.env["mrp.bom.line"]
                .search([("component_template_id", "=", template._origin.id)])
                .bom_id
            )
            for bom in using_boms:
                bom_attrs = (
                    bom.product_tmpl_id
                    .valid_product_template_attribute_line_ids.attribute_id
                )
                extra = template.attribute_line_ids.attribute_id - bom_attrs
                if extra:
                    raise UserError(
                        _(
                            "This product template is used as a component in the "
                            "BoM for %(bom)s and attribute(s) %(attributes)s are "
                            "not present in that product, and this would break "
                            "the BoM behavior.",
                            bom=bom.display_name,
                            attributes=", ".join(extra.mapped("name")),
                        )
                    )
