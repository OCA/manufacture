# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# Copyright 2019 Andrii Skrypka
# Copyright 2024 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from functools import lru_cache

from odoo import models

from odoo.addons.quality_control_oca.models.qc_trigger_line import _filter_trigger_lines


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, vals):
        if "date" in vals:
            existing_inspections = self.env["qc.inspection"]._get_existing_inspections(
                self
            )
            existing_inspections.write({"date": vals.get("date")})
        return super().write(vals)

    def _get_partner_for_trigger_line(self):
        return self.picking_id.partner_id

    def trigger_inspection(self, timings, partner=False):
        @lru_cache
        def get_qc_trigger(picking_type):
            return (
                self.env["qc.trigger"]
                .sudo()
                .search([("picking_type_id", "=", picking_type.id)])
            )

        self.ensure_one()
        inspection_model = self.env["qc.inspection"].sudo()
        trigger_lines = set()
        qc_triggers = get_qc_trigger(self.picking_type_id)
        for qc_trigger in qc_triggers:
            if qc_trigger.partner_selectable:
                partner = partner or self._get_partner_for_trigger_line()
            else:
                partner = False
            for model in [
                "qc.trigger.product_category_line",
                "qc.trigger.product_template_line",
                "qc.trigger.product_line",
            ]:
                trigger_lines = trigger_lines.union(
                    self.env[model]
                    .sudo()
                    .get_trigger_line_for_product(
                        qc_trigger, timings, self.product_id.sudo(), partner=partner
                    )
                )
        for trigger_line in _filter_trigger_lines(trigger_lines):
            date = False
            if trigger_line.timing in ["before", "plan_ahead"]:
                # To pass scheduled date to the generated inspection
                date = self.date
            # inspection_model._make_inspection(self, trigger_line, date=date)
            inspection = inspection_model._make_inspection(
                self, trigger_line, date=date
            )
            if self.product_id.tracking != "none":
                if trigger_line.trigger.inspection_per_lot:
                    move_lines = self.move_line_ids
                    for move_line in move_lines:
                        inspection.write(
                            {
                                "lot_id": move_line.lot_id and move_line.lot_id.id,
                                "qty": move_line.quantity,
                            }
                        )
                        if move_line != move_lines[-1]:
                            inspection = inspection.copy()
                            inspection.set_test(trigger_line)
                            inspection.action_todo()

    def _action_confirm(self, merge=True, merge_into=False):
        moves = super()._action_confirm(merge=merge, merge_into=merge_into)
        for move in moves:
            move.trigger_inspection(["before", "plan_ahead"])
        return moves
