# Copyright 2015-22 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import operator as py_operator

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpBom(models.Model):
    _inherit = "mrp.bom"
    _order = "sequence, code, product_default_code, id"

    @api.depends("bom_line_ids.bom_id", "product_id", "product_tmpl_id")
    def _compute_product_has_other_bom(self):
        for bom in self:
            if bom.product_id:
                bom_ids = self.env["mrp.bom"].search(
                    [("product_id", "=", bom.product_id.id), ("id", "!=", bom.id)],
                )
            else:
                bom_ids = self.env["mrp.bom"].search(
                    [
                        ("product_tmpl_id", "=", bom.product_tmpl_id.id),
                        ("id", "!=", bom.id),
                    ],
                )
            if bom_ids:
                bom.product_has_other_bom = True
            else:
                bom.product_has_other_bom = False

    @api.depends("bom_line_ids.bom_id", "product_id", "product_tmpl_id")
    def _compute_parent_bom_ids(self):
        for bom in self:
            parent_bom_line_ids = self.env["mrp.bom.line"]._bom_line_find(
                product_tmpl=bom.product_id.product_tmpl_id or bom.product_tmpl_id,
                product=bom.product_id,
            )
            if parent_bom_line_ids:
                bom.parent_bom_ids = parent_bom_line_ids.bom_id
                bom.has_parent = True
            else:
                bom.parent_bom_ids = False
                bom.has_parent = False

    @api.depends("bom_line_ids.bom_id", "bom_line_ids.product_id")
    def _compute_child_bom_ids(self):
        for bom in self:
            bom_line_ids = bom.bom_line_ids
            bom.child_bom_ids = bom_line_ids.child_bom_id
            bom.has_child = bool(bom.child_bom_ids)

    def _search_has_child(self, operator, value):
        if operator not in ["=", "!="]:
            raise UserError(_("This operator is not supported"))
        if value == "True":
            value = True
        elif value == "False":
            value = False
        if not isinstance(value, bool):
            raise UserError(_("Value should be True or False (not %s)") % value)
        ops = {"=": py_operator.eq, "!=": py_operator.ne}
        ids = []
        for bom in self.search([]):
            if ops[operator](value, bom.has_child):
                ids.append(bom.id)
        return [("id", "in", ids)]

    def _search_has_parent(self, operator, value):
        if operator not in ["=", "!="]:
            raise UserError(_("This operator is not supported"))
        if value == "True":
            value = True
        elif value == "False":
            value = False
        if not isinstance(value, bool):
            raise UserError(_("Value should be True or False (not %s)") % value)
        ops = {"=": py_operator.eq, "!=": py_operator.ne}
        ids = []
        for bom in self.search([]):
            if ops[operator](value, bom.has_parent):
                ids.append(bom.id)
        return [("id", "in", ids)]

    @api.depends(
        "product_id",
        "product_id.default_code",
        "product_id.product_tmpl_id.default_code",
        "product_tmpl_id.default_code",
    )
    def _compute_internal_reference(self):
        for bom in self:
            bom.product_default_code = (
                bom.product_id.default_code
                or bom.product_id.product_tmpl_id.default_code
                or bom.product_tmpl_id.default_code
            )

    child_bom_ids = fields.One2many("mrp.bom", compute="_compute_child_bom_ids")
    parent_bom_ids = fields.One2many("mrp.bom", compute="_compute_parent_bom_ids")
    has_child = fields.Boolean(
        string="Has components",
        compute="_compute_child_bom_ids",
        search="_search_has_child",
    )
    has_parent = fields.Boolean(
        string="Is component",
        compute="_compute_parent_bom_ids",
        search="_search_has_parent",
    )
    product_has_other_bom = fields.Boolean(
        string="Product has other BoMs",
        compute="_compute_product_has_other_bom",
    )
    product_default_code = fields.Char(
        string="Internal Reference",
        compute="_compute_internal_reference",
        store="True",
    )

    def action_open_child_tree_view(self):
        self.ensure_one()
        res = self.env["ir.actions.actions"]._for_xml_id("mrp.mrp_bom_form_action")
        res["context"] = {"default_bom_line_ids": self.bom_line_ids.ids}
        if self.child_bom_ids:
            res["domain"] = (
                "[('id', 'in', [" + ",".join(map(str, self.child_bom_ids.ids)) + "])]"
            )
        return res

    def action_open_parent_tree_view(self):
        self.ensure_one()
        res = self.env["ir.actions.actions"]._for_xml_id("mrp.mrp_bom_form_action")
        if self.parent_bom_ids:
            res["domain"] = (
                "[('id', 'in', [" + ",".join(map(str, self.parent_bom_ids.ids)) + "])]"
            )
        return res

    def action_open_product_other_bom_tree_view(self):
        self.ensure_one()
        if self.product_id:
            product_bom_ids = self.env["mrp.bom"].search(
                [("product_id", "=", self.product_id.id), ("id", "!=", self.id)],
            )
        else:
            product_bom_ids = self.env["mrp.bom"].search(
                [
                    ("product_tmpl_id", "=", self.product_tmpl_id.id),
                    ("id", "!=", self.id),
                ],
            )
        res = self.env["ir.actions.actions"]._for_xml_id("mrp.mrp_bom_form_action")
        if self.product_id:
            res["context"] = {
                "default_product_id": self.product_id.id,
                "default_product_tmpl_id": self.product_id.product_tmpl_id.id,
            }
        elif self.product_tmpl_id:
            res["context"] = {
                "default_product_tmpl_id": self.product_tmpl_id.id,
            }
        res["domain"] = (
            "[('id', 'in', [" + ",".join(map(str, product_bom_ids.ids)) + "])]"
        )
        return res


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    has_bom = fields.Boolean(
        string="Has sub BoM",
        compute="_compute_child_bom_id",
    )

    @api.depends("product_id", "bom_id")
    def _compute_child_bom_id(self):
        super()._compute_child_bom_id()
        for line in self:
            line.has_bom = bool(line.child_bom_id)

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
