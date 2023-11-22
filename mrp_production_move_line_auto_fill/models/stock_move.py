# Copyright 2023 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_auto_fill_flag(self):
        if self.raw_material_production_id:
            return self.raw_material_production_id.auto_fill_operation
        return super()._get_auto_fill_flag()

    def _get_avoid_lot_assignment_flag(self):
        if self.raw_material_production_id:
            return self.raw_material_production_id.picking_type_id.avoid_lot_assignment
        return super()._get_avoid_lot_assignment_flag()
