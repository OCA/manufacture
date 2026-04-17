# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.depends("production_id.production_location_id")
    def _compute_location_id(self):
        res = super()._compute_location_id()
        for move in self:
            production = move.production_id
            if (
                production
                and production.picking_type_id
                and production.picking_type_id.production_location_id
            ):
                move.location_id = production.picking_type_id.production_location_id
        return res

    @api.depends("raw_material_production_id.production_location_id")
    def _compute_location_dest_id(self):
        res = super()._compute_location_dest_id()
        for move in self:
            production = move.raw_material_production_id
            if (
                production
                and production.picking_type_id
                and production.picking_type_id.production_location_id
            ):
                move.location_dest_id = (
                    production.picking_type_id.production_location_id
                )
        return res
