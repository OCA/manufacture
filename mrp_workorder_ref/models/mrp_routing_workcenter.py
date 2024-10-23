# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    ref = fields.Char(string="Reference")

    _sql_constraints = [
        ("ref_uniq", "UNIQUE(bom_id, ref)", "The reference must be unique per BoM!"),
    ]

    @api.depends("ref")
    def _compute_display_name(self):
        # OVERRIDE to add the dependency required by `name_get`
        return super()._compute_display_name()

    def name_get(self):
        # OVERRIDE to include the reference, when set
        res = super().name_get()
        res_new = []
        for record, item in zip(self, res):
            rec_id, name = item
            if record.ref:
                name = f"[{record.ref}] {name}"
            res_new.append((rec_id, name))
        return res_new
