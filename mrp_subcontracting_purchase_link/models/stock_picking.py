# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _prepare_subcontract_mo_vals(self, subcontract_move, bom):
        vals = super()._prepare_subcontract_mo_vals(subcontract_move, bom)
        if subcontract_move.purchase_line_id:
            vals["purchase_line_id"] = subcontract_move.purchase_line_id.id
        return vals
