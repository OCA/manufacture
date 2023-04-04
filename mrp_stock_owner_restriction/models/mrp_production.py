# Copyright 2023 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    owner_id = fields.Many2one(
        "res.partner",
        "Assign Owner",
        readonly=True,
        states={"draft": [("readonly", False)], "confirmed": [("readonly", False)]},
        check_company=True,
        help="Produced products will be assigned to this owner.",
    )
    owner_restriction = fields.Selection(related="picking_type_id.owner_restriction")

    def write(self, vals):
        if "owner_id" in vals:
            for production in self:
                if production.owner_restriction in (
                    "unassigned_owner",
                    "picking_partner",
                ):
                    production.move_line_raw_ids.unlink()
        return super().write(vals)
