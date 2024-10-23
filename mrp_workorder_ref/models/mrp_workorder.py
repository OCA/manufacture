# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    ref = fields.Char(string="Reference")

    _sql_constraints = [
        (
            "ref_uniq",
            "UNIQUE(production_id, ref)",
            "The Work Order Reference must be unique per MO!",
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE to auto-complete the reference from the operation
        for vals in vals_list:
            if "ref" not in vals and vals.get("operation_id"):
                operation_id = vals["operation_id"]
                operation = self.env["mrp.routing.workcenter"].browse(operation_id)
                if operation.ref:
                    vals["ref"] = operation.ref
        return super().create(vals_list)

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
