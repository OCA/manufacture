# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.depends("product_id", "company_id", "picking_type_id")
    def _compute_production_location(self):
        res = super()._compute_production_location()
        for production in self:
            if (
                production.picking_type_id
                and production.picking_type_id.production_location_id
            ):
                production.production_location_id = (
                    production.picking_type_id.production_location_id
                )
        return res

    def _get_move_raw_values(
        self,
        product_id,
        product_uom_qty,
        product_uom,
        operation_id=False,
        bom_line=False,
    ):
        values = super()._get_move_raw_values(
            product_id, product_uom_qty, product_uom, operation_id, bom_line
        )
        if self.picking_type_id and self.picking_type_id.production_location_id:
            values["location_dest_id"] = self.picking_type_id.production_location_id.id
        return values

    def _get_move_finished_values(
        self,
        product_id,
        product_uom_qty,
        product_uom,
        operation_id=False,
        byproduct_id=False,
        cost_share=0,
    ):
        values = super()._get_move_finished_values(
            product_id,
            product_uom_qty,
            product_uom,
            operation_id,
            byproduct_id,
            cost_share,
        )
        if self.picking_type_id and self.picking_type_id.production_location_id:
            values["location_id"] = self.picking_type_id.production_location_id.id
        return values
