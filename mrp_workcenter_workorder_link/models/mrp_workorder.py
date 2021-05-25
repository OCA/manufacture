# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models

# States than we don't want to take account
STATIC_STATES = ["cancel", "done"]

WORKCENTER_ACTION = {
    "res_model": "mrp.workcenter",
    "type": "ir.actions.act_window",
    "target": "current",
}


class MrpProductionWorkcenterLine(models.Model):
    _inherit = "mrp.production.workcenter.line"
    _order = "sequence ASC, name ASC"

    def button_workcenter(self):
        self.ensure_one()
        view = self.env.ref("mrp.mrp_workcenter_view")
        action = {
            "view_id": view.id,
            "res_id": self.workcenter_id.id,
            "name": "'%s' Workcenter" % self.name,
            "view_mode": "form",
        }
        action.update(WORKCENTER_ACTION)
        return action
