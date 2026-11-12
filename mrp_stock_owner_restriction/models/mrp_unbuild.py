# Copyright 2023 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    def action_validate(self):
        owner_restriction = self.mo_id.owner_restriction
        owner = self.mo_id.owner_id
        if owner and owner_restriction in ("unassigned_owner", "picking_partner"):
            self = self.with_context(force_restricted_owner_id=owner)
        return super().action_validate()
