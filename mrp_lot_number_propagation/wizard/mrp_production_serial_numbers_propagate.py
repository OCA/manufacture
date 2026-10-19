# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models
from odoo.exceptions import UserError


class MrpBatchProducePropagate(models.TransientModel):
    _name = "mrp.production.serials.propagate"
    _description = "Batch production with lot number propagation"

    production_ids = fields.Many2many("mrp.production", readonly=True)

    def action_apply(self):
        self.ensure_one()
        for production in self.production_ids:
            batch_produce_wizard = (
                self.env["mrp.production.serials"]
                .with_context(default_production_id=production.id)
                .create({})
            )
            propagate_move = production._get_propagating_component_move()
            serial_numbers = [
                f"{ml.lot_id.name}{batch_produce_wizard.component_separator}{ml.lot_id.name}"
                for ml in propagate_move.move_line_ids
                if ml.lot_id
            ]
            if not serial_numbers:
                raise UserError(
                    self.env._(
                        "Cannot mass produce without any propagating component line "
                        "having serial number defined."
                    )
                )
            batch_produce_wizard.serial_numbers = "\n".join(serial_numbers)
            batch_produce_wizard.with_context(lot_propagation=True).action_apply()
        return True
