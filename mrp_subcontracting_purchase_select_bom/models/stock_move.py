# Copyright 2024 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_subcontract_bom(self):
        self.ensure_one()
        if self.purchase_line_id and self.purchase_line_id.bom_id:
            return self.purchase_line_id.bom_id
        return super()._get_subcontract_bom()
