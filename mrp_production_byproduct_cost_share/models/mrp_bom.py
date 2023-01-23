# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def _check_bom_lines(self):
        res = super()._check_bom_lines()
        for bom in self:
            for byproduct in bom.byproduct_ids:
                if bom.product_id:
                    same_product = bom.product_id == byproduct.product_id
                else:
                    same_product = (
                        bom.product_tmpl_id == byproduct.product_id.product_tmpl_id
                    )
                if same_product:
                    raise ValidationError(
                        _("By-product %s should not be the same as BoM product.")
                        % bom.display_name
                    )
                if byproduct.cost_share < 0:
                    raise ValidationError(
                        _("By-products cost shares must be positive.")
                    )
            if sum(bom.byproduct_ids.mapped("cost_share")) > 100:
                raise ValidationError(
                    _("The total cost share for a BoM's by-products cannot exceed 100.")
                )
        return res


class MrpByProduct(models.Model):
    _inherit = "mrp.bom.byproduct"

    cost_share = fields.Float(
        "Cost Share (%)",
        digits=(5, 2),
        help="The percentage of the final production cost for this by-product line"
        " (divided between the quantity produced)."
        "The total of all by-products' cost share must be less than or equal to 100.",
    )
