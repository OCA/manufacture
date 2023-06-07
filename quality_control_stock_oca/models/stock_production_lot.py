# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.lot"

    qc_inspections_ids = fields.One2many(
        comodel_name="qc.inspection",
        inverse_name="lot_id",
        copy=False,
        string="Inspections",
        help="Inspections related to this lot.",
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
                ["lot_id", "state"],
                ["lot_id", "state"],
                lazy=False,
            )
        )
        lot_data = {}
        for d in data:
            lot_data.setdefault(d["lot_id"][0], {}).setdefault(d["state"], 0)
            lot_data[d["lot_id"][0]][d["state"]] += d["__count"]
        for lot in self:
            count_data = lot_data.get(lot.id, {})
            lot.created_inspections = sum(count_data.values())
            lot.passed_inspections = count_data.get("success", 0)
            lot.failed_inspections = count_data.get("failed", 0)
            lot.done_inspections = lot.passed_inspections + lot.failed_inspections
