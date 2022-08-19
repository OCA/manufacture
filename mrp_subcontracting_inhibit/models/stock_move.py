# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_subcontract_bom(self):
        """Hack to simulate that there is no subcontracting BoM."""
        self.ensure_one()
        if self.purchase_line_id.subcontracting_inhibit:
            return False
        return super()._get_subcontract_bom()
