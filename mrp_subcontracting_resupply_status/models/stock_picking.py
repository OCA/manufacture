# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    resupply_status = fields.Selection(
        [
            ("pending", "Not Resupplied"),
            ("partial", "Partially Resupplied"),
            ("full", "Fully Resupplied"),
        ],
        compute="_compute_resupply_status",
        store=True,
    )

    subcontracting_resupply_picking_count = fields.Integer(
        "Count of Subcontracting Resupply",
        compute="_compute_subcontracting_resupply_picking_count",
        help="Count of Subcontracting Resupply related to this receipt",
    )

    @api.depends("move_ids")
    def _compute_subcontracting_resupply_picking_count(self):
        for picking in self:
            picking.subcontracting_resupply_picking_count = len(
                picking._get_subcontracting_resupplies()
            )

    @api.depends(
        "move_ids.is_subcontract",
        "move_ids.move_orig_ids.production_id.production_group_id",
    )
    def _compute_resupply_status(self):
        for picking in self:
            picking.resupply_status = (
                picking._get_subcontracting_resupplies()._get_resupply_status()
            )

    def _get_subcontracting_resupplies(self):
        """Get the resupply pickings of the subcontract moves of this receipt."""
        return self._get_resupplies_of_subcontract_moves(self.move_ids)

    @api.model
    def _get_resupplies_of_subcontract_moves(self, moves):
        groups = moves.filtered(
            "is_subcontract"
        ).move_orig_ids.production_id.production_group_id
        if not groups:
            return self.browse()
        pickings = self.search([("move_ids.production_group_id", "in", groups.ids)])
        return pickings.filtered(
            lambda p: any(m.location_dest_id.is_subcontract() for m in p.move_ids)
        )

    def _get_resupply_status(self):
        """Resupply status of the resupply pickings in self."""
        if all(r.state == "cancel" for r in self):
            return False
        if all(r.state in ["done", "cancel"] for r in self):
            return "full"
        if any(r.state == "done" for r in self):
            return "partial"
        return "pending"
