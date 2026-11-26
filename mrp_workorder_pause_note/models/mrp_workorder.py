# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    last_pause_note = fields.Text(
        help="Last pause note given to the operator in this workorder.",
        compute="_compute_last_pause_note_data",
    )

    last_pause_note_user_id = fields.Many2one(
        "res.users",
        string="Last Pause Note User",
        help="User who created the last pause note.",
        compute="_compute_last_pause_note_data",
    )

    @api.depends("time_ids.pause_note", "time_ids.user_id", "state")
    def _compute_last_pause_note_data(self):
        wo_progress = self.filtered(
            lambda x: x.time_ids.filtered("date_end") and x.state == "progress"
        )
        for workorder in wo_progress:
            last_time = workorder.time_ids.filtered(lambda t: t.date_end).sorted(
                lambda t: t.date_end
            )[-1]
            workorder.update(
                {
                    "last_pause_note": last_time.pause_note,
                    "last_pause_note_user_id": last_time.user_id.id,
                }
            )
        (self - wo_progress).update(
            {
                "last_pause_note": False,
                "last_pause_note_user_id": False,
            }
        )

    def button_pending(self):
        if len(self) != 1 or self.env.context.get(
            "mrp_wo_skip_pause_note_request", False
        ):
            return super().button_pending()
        else:
            return {
                "type": "ir.actions.act_window",
                "name": _("Pause Note"),
                "res_model": "mrp.workorder.pause.note.wizard",
                "view_mode": "form",
                "target": "new",
                "context": {
                    "default_workorder_id": self.id,
                    "default_previous_note": self.last_pause_note,
                },
            }
