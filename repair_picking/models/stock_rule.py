# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_custom_move_fields(self):
        fields = super(StockRule, self)._get_custom_move_fields()
        # Fields is added on `repair_stock_move` module.
        fields += ["repair_line_id"]
        return fields


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _get_rule_domain(self, location, values):
        domain = super(ProcurementGroup, self)._get_rule_domain(location, values)
        if values.get("source_repair_location_id"):
            domain.append(("location_src_id", "=", values.get('source_repair_location_id')))
        return domain
