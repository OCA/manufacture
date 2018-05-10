# Copyright 2018 Tecnativa - David Vidal
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _run_manufacture(self, product_id, product_qty, product_uom,
                         location_id, name, origin, values):
        return super(
            ProcurementRule, self.with_context(group_mo_by_product=True),
        )._run_manufacture(
            product_id, product_qty, product_uom, location_id, name, origin,
            values,
        )
