# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
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
        done_moves = self.mapped("move_finished_ids").filtered(
            lambda r: r.state == "done"
        )
        res = super()._post_inventory(cancel_backorder=cancel_backorder)
        inspection_model = self.env["qc.inspection"]
        new_done_moves = (
            self.mapped("move_finished_ids").filtered(lambda r: r.state == "done")
            - done_moves
        )
        if new_done_moves:
            qc_trigger = self.env.ref("quality_control_mrp_oca.qc_trigger_mrp")
        for move in new_done_moves:
            trigger_lines = set()
            for model in [
                "qc.trigger.product_category_line",
                "qc.trigger.product_template_line",
                "qc.trigger.product_line",
            ]:
                trigger_lines = trigger_lines.union(
                    self.env[model].get_trigger_line_for_product(
                        qc_trigger, ["after"], move.product_id
                    )
                )
            for trigger_line in _filter_trigger_lines(trigger_lines):
                inspection_model._make_inspection(move, trigger_line)
        return res
