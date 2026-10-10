# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpWorkorderPauseNoteWizard(models.TransientModel):
    _name = "mrp.workorder.pause.note.wizard"
    _description = "Workorder Pause Note Wizard"

    workorder_id = fields.Many2one("mrp.workorder")
    previous_note = fields.Text(
        readonly=True,
    )
    note = fields.Text(
        string="Pause Note",
        required=True,
    )

    def action_confirm(self):
        self.ensure_one()
        wo = self.workorder_id
        timeline = self.workorder_id.time_ids.filtered(
            lambda x: x.user_id == self.env.user and not x.date_end
        )[:1]
        if timeline:
            timeline.pause_note = self.note
        wo.with_context(mrp_wo_skip_pause_note_request=True).button_pending()
        return {"type": "ir.actions.act_window_close"}
