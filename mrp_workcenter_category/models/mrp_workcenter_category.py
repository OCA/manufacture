# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MrpWorkcenterCategory(models.Model):
    _name = "mrp.workcenter.category"
    _description = "Work Center Category"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = "complete_name"
    _order = "complete_name"

    ref = fields.Char(string="Internal Reference", index=True)
    name = fields.Char(required=True)
    parent_path = fields.Char(index=True)
    parent_id = fields.Many2one(
        string="Parent Category",
        comodel_name="mrp.workcenter.category",
        ondelete="cascade",
        index=True,
    )
    child_ids = fields.One2many(
        string="Children Categories",
        comodel_name="mrp.workcenter.category",
        inverse_name="parent_id",
    )
    complete_name = fields.Char(
        compute="_compute_complete_name",
        store=True,
        recursive=True,
    )
    description = fields.Html()

    _sql_constraints = [
        ("ref_uniq", "UNIQUE(ref)", "The reference must be unique!"),
    ]

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for rec in self:
            if rec.parent_id:
                rec.complete_name = f"{rec.parent_id.complete_name} / {rec.name}"
            else:
                rec.complete_name = rec.name

    @api.model
    def name_create(self, name):
        # OVERRIDE: `name_create` should ignore `_rec_name = "complete_name"`
        record = self.create({"name": name})
        return record.name_get()[0]
