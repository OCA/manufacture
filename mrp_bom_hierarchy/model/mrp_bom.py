# Copyright 2015-22 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import operator as py_operator

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpBom(models.Model):
    _inherit = "mrp.bom"

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
