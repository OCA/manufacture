# Copyright 2022 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from random import randint

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpTag(models.Model):
    _name = "mrp.tag"
    _description = "MRP Tag"
    _parent_store = True

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char("Tag Name", required=True, translate=True)
    color = fields.Integer(default=lambda self: self._get_default_color())
    parent_id = fields.Many2one("mrp.tag", index=True, ondelete="cascade")
    child_ids = fields.One2many("mrp.tag", "parent_id")
    parent_path = fields.Char(index=True, unaccent=False)

    _sql_constraints = [
        ("tag_name_uniq", "unique (name)", "Tag name already exists !"),
    ]

    @api.depends("name", "parent_id")
    def _compute_display_name(self):
        for tag in self:
            names = []
            current = tag
            while current.name:
                names.append(current.name)
                current = current.parent_id
            tag.display_name = " / ".join(reversed(names))

    @api.model
    def _name_search(self, name, domain=None, operator="ilike", limit=None, order=None):
        if name:
            domain = [("name", operator, name.split(" / ")[-1])] + list(domain or [])
        return super()._name_search(
            name=name,
            domain=domain,
            operator=operator,
            limit=limit,
            order=order,
        )

    @api.constrains("parent_id")
    def _check_parent_recursion(self):
        if not self._check_recursion("parent_id"):
            raise ValidationError(_("Tags cannot be recursive."))
