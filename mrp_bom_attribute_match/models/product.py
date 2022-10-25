from odoo import _, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            rec._check_product_with_component_change_allowed()
            rec._check_component_change_allowed()
        return res

    def _check_product_with_component_change_allowed(self):
        self.ensure_one()
        if len(self.attribute_line_ids) > 0 and len(self.bom_ids) > 0:
            for bom in self.bom_ids:
                for line in bom.bom_line_ids.filtered(
                    lambda x: x.match_on_attribute_ids
                ):
                    prod_attr_ids = self.attribute_line_ids.attribute_id.filtered(
                        lambda x: x.create_variant != "no_variant"
                    ).ids
                    comp_attr_ids = line.match_on_attribute_ids.ids
                    diff = list(set(comp_attr_ids) - set(prod_attr_ids))
                    if len(diff) > 0:
                        attr_recs = self.env["product.attribute"].browse(diff)
                        raise UserError(
                            _(
                                "The attributes you're trying to remove are used in "
                                "the BoM as a match with Component (Product Template). "
                                "To remove these attributes, first remove the BOM line "
                                "with the matching component.\n"
                                "Attributes: %(attributes)s\nBoM: %(bom)s",
                                attributes=", ".join(attr_recs.mapped("name")),
                                bom=bom.display_name,
                            )
                        )

    def _check_component_change_allowed(self):
        self.ensure_one()
        if len(self.attribute_line_ids) > 0:
            boms = self._get_component_boms()
            if boms:
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
