# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.onchange("product_id", "move_raw_ids")
    def _onchange_product_id(self):
        # `never_product_template_attribute_value_ids` is a core M2M field on
        # `mrp.production`. Including it here triggers a duplicate relation setup
        # and breaks registry initialization.
        if self.company_id.allow_same_product_component_finish:
            return
        return super()._onchange_product_id()
