# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _prepare_subcontract_mo_vals(self, subcontract_move, bom):
        vals = super()._prepare_subcontract_mo_vals(subcontract_move, bom)
        vals["owner_id"] = subcontract_move.picking_id.owner_id.id
        return vals
