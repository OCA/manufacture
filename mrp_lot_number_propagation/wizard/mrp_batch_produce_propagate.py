# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class MrpBatchProducePropagate(models.TransientModel):
    _name = "mrp.batch.produce.propagate"
    _description = "Batch production with lot number propagation"

    production_ids = fields.Many2many("mrp.production", readonly=True)

    def action_prepare(self):
        return self._batch_produce(mark_done=False)

    def action_done(self):
        return self._batch_produce(mark_done=True)

    def _batch_produce(self, mark_done=False):
        self.ensure_one()
        for production in self.production_ids:
            batch_produce_wizard = (
                self.env["mrp.batch.produce"]
                .with_context(default_production_id=production.id)
                .create({})
            )
            propagate_move = production._get_propagating_component_move()
            batch_produce_wizard.production_text = "\n".join(
                [
                    f"{ml.lot_id.name}{batch_produce_wizard.component_separator}{ml.lot_id.name}"
                    for ml in propagate_move.move_line_ids
                    if ml.lot_id
                ]
            )
            batch_produce_wizard.with_context(
                lot_propagation=True
            )._production_text_to_object(mark_done=mark_done)
        return True
