# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    def action_bom_component_mass_change(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mrp_bom_component_mass_change.mrp_bom_component_mass_change_action"
        )
        action["context"] = {
            "default_component_id": self.product_id.id,
            "default_component_locked": True,
        }
        return action
