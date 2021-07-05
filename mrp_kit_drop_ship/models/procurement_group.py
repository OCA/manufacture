# Copyright 2021 Forgeflow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, procurements):
        other_procurements = []
        for procurement in procurements:
            rule = self._get_rule(
                procurement.product_id, procurement.location_id, procurement.values
            )
            if (
                rule.location_id.usage == "customer"
                and rule.location_src_id.usage == "supplier"
            ):
                return super(ProcurementGroup, self.with_context(ignore_kit=True)).run(
                    [procurement]
                )
            other_procurements.append(procurement)
        return super(ProcurementGroup, self).run(other_procurements)
