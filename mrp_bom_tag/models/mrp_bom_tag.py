# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from random import randint

from odoo import api, fields, models


class MrpBomTag(models.Model):
    _name = "mrp.bom.tag"
    _description = "Bill Of Material Tag"
    _parent_name = "parent_id"
    _parent_store = True
    _order = "complete_name"

    def _default_color(self):
        return randint(1, 11)

    # Column Section
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda s: s._default_company_id(),
    )

    name = fields.Char(required=True)
    color = fields.Integer(default=lambda self: self._default_color())
    complete_name = fields.Char(
        compute="_compute_complete_name", store=True, recursive=True
    )

    parent_id = fields.Many2one(
        "mrp.bom.tag", "Parent BoM Tag", index=True, ondelete="cascade"
    )
    parent_path = fields.Char(index=True, unaccent=False)
    child_id = fields.One2many("mrp.bom.tag", "parent_id", "Child Categories")

    bom_ids = fields.Many2many(
        comodel_name="mrp.bom",
    )

    bom_qty = fields.Integer(
        "BoM Quantity",
        compute="_compute_bom_qty",
        help="Number of BoMs under this BoM tag (not considering children categories)",
    )

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for bom_tag in self:
            if bom_tag.parent_id:
                bom_tag.complete_name = "%s / %s" % (
                    bom_tag.parent_id.complete_name,
                    bom_tag.name,
                )
            else:
                bom_tag.complete_name = bom_tag.name

    @api.depends("bom_ids")
    def _compute_bom_qty(self):
        for bom_tag in self:
            bom_tag.bom_qty = len(bom_tag.bom_ids)

    # Model Section
    @api.model
    def _default_company_id(self):
        return self.env.company.id

    # Name Section
    def name_get(self):
        result = []
        for record in self:
            if self.env.context.get("display_complete_name", False):
                result.append((record.id, record.complete_name))
            else:
                result.append((record.id, record.name))
        return result
