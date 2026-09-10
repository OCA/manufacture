from odoo import Command, _, api, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains("attribute_line_ids")
    def _check_product_with_component_change_allowed(self):
        for rec in self:
            if not rec.attribute_line_ids:
                continue
            for bom in rec.bom_ids:
                for line in bom.bom_line_ids.filtered("match_on_attribute_ids"):
                    prod_attr_ids = rec.attribute_line_ids.attribute_id.filtered(
                        lambda x: x.create_variant != "no_variant"
                    ).ids
                    comp_attr_ids = line.match_on_attribute_ids.ids
                    diff_ids = list(set(comp_attr_ids) - set(prod_attr_ids))
                    diff = rec.env["product.attribute"].browse(diff_ids)
                    if diff:
                        raise UserError(
                            _(
                                "The attributes you're trying to remove are used in "
                                "the BoM as a match with Component (Product Template). "
                                "To remove these attributes, first remove the BOM line "
                                "with the matching component.\n"
                                "Attributes: %(attributes)s\nBoM: %(bom)s",
                                attributes=", ".join(diff.mapped("name")),
                                bom=bom.display_name,
                            )
                        )

    @api.constrains("attribute_line_ids")
    def _check_component_change_allowed(self):
        for rec in self:
            if not rec.attribute_line_ids:
                continue
            boms = self._get_component_boms()
            if not boms:
                continue
            for bom in boms:
                vpa = bom.product_tmpl_id.valid_product_template_attribute_line_ids
                prod_attr_ids = vpa.attribute_id.ids
                comp_attr_ids = self.attribute_line_ids.attribute_id.ids
                diff = list(set(comp_attr_ids) - set(prod_attr_ids))
                if len(diff) > 0:
                    attr_recs = self.env["product.attribute"].browse(diff)
                    raise UserError(
                        _(
                            "This product template is used as a component in the "
                            "BOMs for %(bom)s and attribute(s) %(attributes)s is "
                            "not present in all such product(s), and this would "
                            "break the BOM behavior.",
                            attributes=", ".join(attr_recs.mapped("name")),
                            bom=bom.display_name,
                        )
                    )

    def _get_component_boms(self):
        self.ensure_one()
        bom_lines = self.env["mrp.bom.line"].search(
            [("component_template_id", "=", self._origin.id)]
        )
        if bom_lines:
            return bom_lines.mapped("bom_id")
        return False


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _compute_bom_price(self, bom, boms_to_recompute=False, byproduct_bom=False):
        self.ensure_one()
        # OVERRIDE to fill in the `line.product_id` if a component template is used.
        # To avoid a complete override, we HACK the bom by replacing it with a virtual
        # record, and modifying it's lines on-the-fly.
        has_template_lines = any(
            line.component_template_id for line in bom.bom_line_ids
        )
        if has_template_lines:
            bom = bom.new(origin=bom)
            to_ignore_line_ids = []
            for line in bom.bom_line_ids:
                if line._skip_bom_line(self) or not line.component_template_id:
                    continue
                line_product = bom._get_component_template_product(
                    line, self, line.product_id
                )
                if not line_product:
                    to_ignore_line_ids.append(line.id)
                    continue
                else:
                    line.product_id = line_product
            if to_ignore_line_ids:
                bom.bom_line_ids = [Command.unlink(id) for id in to_ignore_line_ids]
        return super()._compute_bom_price(bom, boms_to_recompute, byproduct_bom)
