# Copyright 2026 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_confirm(self):
        for production in self:
            # Check if BOM is outdated before allowing confirmation
            if production.is_outdated_bom:
                raise (
                    UserError(
                        "Cannot confirm production order '%s'. "
                        "The BOM is outdated. Please update the BOM "
                        "or create a new production order."
                    )
                    % production.name
                )

        return super().action_confirm()
