# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# Copyright 2026 FactorLibre - Adriana Saiz <adriana.saiz@factorlibre.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.quality_control_oca.models.qc_trigger_line import _filter_trigger_lines


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.depends("qc_inspections_ids")
    def _compute_created_inspections(self):
        for production in self:
            production.created_inspections = len(production.qc_inspections_ids)

    qc_inspections_ids = fields.One2many(
        comodel_name="qc.inspection",
        inverse_name="production_id",
        copy=False,
        string="Inspections",
        help="Inspections related to this production.",
    )
    created_inspections = fields.Integer(
        compute="_compute_created_inspections", string="Created inspections"
    )

    def _post_inventory(self, cancel_backorder=False):
        res = super()._post_inventory(cancel_backorder=cancel_backorder)
        # Transition plan inspections to ready (same as stock.picking._action_done)
        plan_inspections = self.sudo().qc_inspections_ids.filtered(
            lambda x: x.state == "plan"
        )
        plan_inspections.write({"state": "ready", "date": fields.Datetime.now()})
        # Create "after" inspections for newly done finished moves
        for production in self:
            production._trigger_after_qc_inspections()
        return res

    def _trigger_after_qc_inspections(self):
        """Trigger QC inspections with 'after' timing for finished moves.

        Reuses stock.move.trigger_inspection() to stay consistent with
        the picking type trigger mechanism from quality_control_stock_oca.
        Falls back to qc_trigger_mrp for backward compatibility.
        """
        self.ensure_one()
        inspection_model = self.env["qc.inspection"].sudo()
        done_moves = self.move_finished_ids.filtered(lambda m: m.state == "done")
        for move in done_moves:
            existing = inspection_model._get_existing_inspections(move)
            if existing.filtered(lambda i: i.timing == "after"):
                continue
            # Use picking type trigger (consistent with before/plan_ahead)
            move.trigger_inspection(["after"])
            # Fallback: if nothing was created, try with qc_trigger_mrp
            if not inspection_model._get_existing_inspections(move).filtered(
                lambda i: i.timing == "after"
            ):
                self._trigger_mrp_qc_fallback(move)

    def _trigger_mrp_qc_fallback(self, move):
        """Fallback for clients with trigger lines configured on qc_trigger_mrp."""
        qc_trigger = self.env.ref(
            "quality_control_mrp_oca.qc_trigger_mrp", raise_if_not_found=False
        )
        if not qc_trigger:
            return
        trigger_lines = set()
        for model in self.env["qc.trigger.line"].get_trigger_line_models():
            trigger_lines = trigger_lines.union(
                self.env[model].get_trigger_line_for_product(
                    qc_trigger, ["after"], move.product_id
                )
            )
        inspection_model = self.env["qc.inspection"]
        for trigger_line in _filter_trigger_lines(trigger_lines):
            inspection_model._make_inspection(move, trigger_line)

    def action_cancel(self):
        res = super().action_cancel()
        self.sudo().qc_inspections_ids.filtered(
            lambda x: x.state == "plan"
        ).action_cancel()
        return res
