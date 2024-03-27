# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    mrp_production_request_id = fields.Many2one(
        comodel_name="mrp.production.request",
        string="Manufacturing Request",
        copy=False,
        readonly=True,
    )

    def _get_move_finished_values(
        self,
        product_id,
        product_uom_qty,
        product_uom,
        operation_id=False,
        byproduct_id=False,
    ):
        """`move_dest_ids` is a One2many fields in mrp.production, thus we cannot
        indicate the same destination move in several MOs (which most probably would be
        the case with MRs). Storing them on the MR and writing them on the finished
        moves as it would happen if they were present in the MO, is the best workaround
        without changing the standard data model."""
        values = super()._get_move_finished_values(
            product_id,
            product_uom_qty,
            product_uom,
            operation_id=operation_id,
            byproduct_id=byproduct_id,
        )
        request = self.mrp_production_request_id
        if request and request.move_dest_ids:
            values.update({"move_dest_ids": [(4, x.id) for x in request.move_dest_ids]})
        return values
