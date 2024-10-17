# Copyright 2023 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    # FIXME handle unbuild cases without MO
    # owner_id = fields.Many2one(
    #     "res.partner",
    #     "Assign Owner",
    #     readonly=True,
    #     states={"draft": [("readonly", False)], "confirmed": [("readonly", False)]},
    #     check_company=True,
    #     help="Produced products will be assigned to this owner.",
    # )
    # owner_restriction = fields.Selection(related="picking_type_id.owner_restriction")

    def action_validate(self):
        owner_restriction = self.mo_id.owner_restriction
        owner = self.mo_id.owner_id
        if owner and owner_restriction in ("unassigned_owner", "picking_partner"):
            self = self.with_context(force_restricted_owner_id=owner)
        return super().action_validate()
