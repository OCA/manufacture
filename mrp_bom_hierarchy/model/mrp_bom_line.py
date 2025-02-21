# Copyright 2015-22 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    has_bom = fields.Boolean(
        string="Has sub BoM",
        compute="_compute_has_bom",
    )

    @api.depends("product_id", "bom_id")
    def _compute_has_bom(self):
        # mrp.bom.line _compute_child_bom_id get child bom or return False
        res = super()._compute_child_bom_id()
        for line in self:
            line.has_bom = bool(line.child_bom_id)
        return res

    def action_open_product_bom_tree_view(self):
        self.ensure_one()
        res = self.env["ir.actions.actions"]._for_xml_id("mrp.mrp_bom_form_action")
        res["domain"] = (
            "[('id', 'in', [" + ",".join(map(str, self.child_bom_id.ids)) + "])]"
        )
        return res

    @api.model
    def _bom_line_find_domain(
        self,
        product_tmpl=None,
        product=None,
        picking_type=None,
        company_id=False,
        bom_type=False,
    ):
        if product:
            if not product_tmpl:
                product_tmpl = product.product_tmpl_id
            domain = [
                "|",
                ("product_id", "=", product.id),
                "&",
                ("product_id", "=", False),
                ("product_tmpl_id", "=", product_tmpl.id),
            ]
        elif product_tmpl:
            domain = [("product_tmpl_id", "=", product_tmpl.id)]
        else:
            # neither product nor template, makes no sense to search
            raise UserError(
                _(
                    "You should provide either a product or "
                    "a product template to search a BoM Line"
                )
            )
        if picking_type:
            domain += [
                "|",
                ("bom_id.picking_type_id", "=", picking_type.id),
                ("bom_id.picking_type_id", "=", False),
            ]
        if company_id or self.env.context.get("company_id"):
            domain = domain + [
                "|",
                ("company_id", "=", False),
                ("company_id", "=", company_id or self.env.context.get("company_id")),
            ]
        if bom_type:
            domain += [("bom_id.type", "=", bom_type)]
        # order to prioritize bom line with product_id over the one without
        return domain

    @api.model
    def _bom_line_find(
        self,
        product_tmpl=None,
        product=None,
        picking_type=None,
        company_id=False,
        bom_type=False,
    ):
        """Finds BoM lines for particular product, picking and company"""
        if (
            product
            and product.type == "service"
            or product_tmpl
            and product_tmpl.type == "service"
        ):
            return self.env["mrp.bom.line"]
        domain = self._bom_line_find_domain(
            product_tmpl=product_tmpl,
            product=product,
            picking_type=picking_type,
            company_id=company_id,
            bom_type=bom_type,
        )
        if domain is False:
            return self.env["mrp.bom.line"]
        return self.search(domain, order="sequence, product_id")
