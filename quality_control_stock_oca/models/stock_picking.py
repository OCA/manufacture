# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# Copyright 2019 Andrii Skrypka
# Copyright 2024 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    qc_inspections_ids = fields.One2many(
        comodel_name="qc.inspection",
        inverse_name="picking_id",
        copy=False,
        string="Inspections",
        help="Inspections related to this picking.",
    )
    created_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Created inspections"
    )
    done_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Done inspections"
    )
    passed_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Inspections OK"
    )
    failed_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Inspections failed"
    )

    @api.depends("qc_inspections_ids", "qc_inspections_ids.state")
    def _compute_count_inspections(self):
        data = (
            self.env["qc.inspection"]
            .sudo()
            .read_group(
                [("id", "in", self.mapped("qc_inspections_ids").ids)],
                ["picking_id", "state"],
                ["picking_id", "state"],
                lazy=False,
            )
        )
        picking_data = {}
        for d in data:
            picking_data.setdefault(d["picking_id"][0], {}).setdefault(d["state"], 0)
            picking_data[d["picking_id"][0]][d["state"]] += d["__count"]
        for picking in self:
            count_data = picking_data.get(picking.id, {})
            picking.created_inspections = sum(count_data.values())
            picking.passed_inspections = count_data.get("success", 0)
            picking.failed_inspections = count_data.get("failed", 0)
            picking.done_inspections = (
                picking.passed_inspections + picking.failed_inspections
            )

    def trigger_inspections(self, timings):
        """Triggers the creation of or an update on inspections for attached stock moves

        :param: timings: list of timings among 'before', 'after' and 'plan_ahead'
        """
        self.ensure_one()
        moves_with_inspections = self.env["stock.move"]
        existing_inspections = self.env["qc.inspection"]._get_existing_inspections(
            self.move_ids
        )
        for inspection in existing_inspections:
            inspection.onchange_object_id()
            moves_with_inspections += inspection.object_id
        for operation in self.move_ids - moves_with_inspections:
            operation.trigger_inspection(timings, self.partner_id)

    def action_cancel(self):
        res = super().action_cancel()
        self.qc_inspections_ids.filtered(lambda x: x.state == "plan").action_cancel()
        return res

    def _action_done(self):
        res = super()._action_done()
        plan_inspections = self.qc_inspections_ids.filtered(lambda x: x.state == "plan")
        plan_inspections.write({"state": "ready", "date": fields.Datetime.now()})
        for picking in self:
            picking.trigger_inspections(["after"])
        return res

    def _create_backorder(self):
        res = super()._create_backorder()
        # To re-allocate backorder moves to the new backorder picking
        self.qc_inspections_ids._compute_picking()
        return res
