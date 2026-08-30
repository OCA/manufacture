# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    restore_rm_stock_in_origin_loc = fields.Boolean(
        string="Return Components to Original Location",
        help="If selected, components will be returned to the same location"
        " they were taken from during manufacturing.",
    )

    def action_unbuild(self):
        self.ensure_one()
        if self.mo_id and self.restore_rm_stock_in_origin_loc:
            self = self.with_context(exact_location=True)
        return super().action_unbuild()

    def _prepare_move_line_vals(self, move, origin_move_line, taken_quantity):
        vals = super()._prepare_move_line_vals(move, origin_move_line, taken_quantity)
        if self.env.context.get("exact_location"):
            vals["location_id"] = origin_move_line.location_dest_id.id
            vals["location_dest_id"] = origin_move_line.location_id.id
        return vals
