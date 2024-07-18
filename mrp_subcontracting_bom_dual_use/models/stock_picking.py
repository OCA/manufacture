# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _subcontracted_produce(self, subcontract_details):
        """Add a context for the subcontracts created by this method."""
        self = self.with_context(force_subcontract_create_workorder=True)
        super()._subcontracted_produce(subcontract_details)
