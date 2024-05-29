# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.exceptions import UserError


class SwitchWorkcenter(models.TransientModel):
    _name = "switch.workcenter"
    _description = "Switch Workcenter onf workorders"

    workcenter_id = fields.Many2one("mrp.workcenter", "Workcenter", required=True)
    parent_workcenter_id = fields.Many2one(
        "mrp.workcenter", "Parent Workcenter", required=True
    )

    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        wos = self.env["mrp.workorder"].browse(self.env.context.get("active_ids", []))
        if any([wo.state in ("done", "cancel") for wo in wos]):
            raise UserError(
                _(
                    "You can not change the workcenter of an in progress or done "
                    "operation"
                )
            )

        workcenter = wos.workcenter_id
        if len(workcenter) != 1:
            raise UserError(
                _(
                    "You can only change the workcenter of workorders belonging to the "
                    "same workcenter"
                )
            )
        parent_level_1_id = workcenter.parent_level_1_id.id
        if not parent_level_1_id:
            raise UserError(
                _(
                    "The present workcenter of the workorders does not belong to any "
                    "group of workcenter. It can't be switched"
                )
            )
        res["parent_workcenter_id"] = workcenter.parent_level_1_id.id
        return res

    def switch_workcenter(self):
        self.ensure_one()
        active_ids = self.env.context.get("active_ids", [])
        vals = {"workcenter_id": self.workcenter_id.id}
        lines = self.env["mrp.workorder"].browse(active_ids)
        lines.write(vals)
        return True
