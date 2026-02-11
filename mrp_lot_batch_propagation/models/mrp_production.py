# Copyright 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    batch_production_ids = fields.Many2many(
        "mrp.production",
        string="Batch Productions",
        help="Production orders that created the batches being consumed"
        " in this production",
        compute="_compute_batch_production_ids",
    )
    batch_bom_ids = fields.Many2many(
        "mrp.bom",
        string="Batch BOMs",
        help="BOMs used for the batches being consumed in this production",
        compute="_compute_batch_bom_ids",
    )

    @api.depends("move_raw_ids.move_line_ids.lot_id.batch_production_id")
    def _compute_batch_production_ids(self):
        """Compute batch productions from consumed lots"""
        for mo in self:
            batch_mo = mo.filtered(lambda x: x.product_id.mrp_batch_propagate_computed)
            raw_batch_mos = mo.move_raw_ids.move_line_ids.lot_id.batch_production_id
            mo.batch_production_ids = raw_batch_mos | batch_mo

    @api.depends("batch_production_ids")
    def _compute_batch_bom_ids(self):
        """Compute batch BOMs from batch productions"""
        for mo in self:
            mo.batch_bom_ids = mo.batch_production_ids.bom_id

    def _set_finished_lot_batch_info(self):
        """Update MRP finished lots with the batch BOMs and production ID"""
        for mo in self.filtered("lot_producing_id"):
            mo.lot_producing_id.batch_production_id = mo.batch_production_ids

    def button_mark_done(self):
        """Override to set batch BOM and production ID on finished lots"""
        result = super().button_mark_done()
        self._set_finished_lot_batch_info()
        return result
