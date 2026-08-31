# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import ast

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    mrp_area_ids = fields.One2many(
        comodel_name="product.mrp.area",
        inverse_name="product_tmpl_id",
        string="MRP Area parameters",
    )
    mrp_area_count = fields.Integer(
        string="MRP Area Parameter Count",
        readonly=True,
        compute="_compute_mrp_area_count",
    )

    def _compute_mrp_area_count(self):
        for rec in self:
            rec.mrp_area_count = len(rec.mrp_area_ids)

    @api.constrains("company_id")
    def _check_mrp_area_parameters_company(self):
        """Products cannot be restricted to a company while they keep MRP area
        parameters belonging to another one: such parameters are not usable and
        break any view showing them, as the product is not readable for the users
        of the parameter's company.
        """
        templates = self.filtered("company_id")
        if not templates:
            return
        parameters = (
            self.env["product.mrp.area"]
            .sudo()
            .with_context(active_test=False)
            .search([("product_tmpl_id", "in", templates.ids)])
        )
        for template in templates:
            wrong_company = parameters.filtered(
                lambda p, t=template: p.product_tmpl_id == t
                and p.company_id
                and not t.filtered_domain(t._check_company_domain(p.company_id))
            )
            if wrong_company:
                raise ValidationError(
                    _(
                        "The product %(product)s has MRP area parameters that "
                        "belong to another company: %(parameters)s.\n"
                        "Delete those parameters before restricting the product "
                        "to the company %(company)s.",
                        product=template.display_name,
                        parameters=", ".join(
                            f"{p.mrp_area_id.display_name} "
                            f"({p.company_id.display_name})"
                            for p in wrong_company
                        ),
                        company=template.company_id.display_name,
                    )
                )

    def action_view_mrp_area_parameters(self):
        self.ensure_one()
        result = self.env["ir.actions.actions"]._for_xml_id(
            "mrp_multi_level.product_mrp_area_action"
        )
        ctx = ast.literal_eval(result.get("context"))
        mrp_areas = self.env["mrp.area"].search([])
        if "context" not in result:
            result["context"] = {}
        if len(mrp_areas) == 1:
            ctx.update({"default_mrp_area_id": mrp_areas[0].id})
        mrp_area_ids = self.with_context(active_test=False).mrp_area_ids.ids
        if len(self.product_variant_ids) == 1:
            variant = self.product_variant_ids[0]
            ctx.update({"default_product_id": variant.id})
        if len(mrp_area_ids) != 1:
            result["domain"] = [("id", "in", mrp_area_ids)]
        else:
            res = self.env.ref("mrp_multi_level.product_mrp_area_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = mrp_area_ids[0]
        result["context"] = ctx
        return result
