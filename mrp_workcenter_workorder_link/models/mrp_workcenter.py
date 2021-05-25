# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

# States than we don't want to take account
STATIC_STATES = ["cancel", "done"]

WORKCENTER_ACTION = {
    "res_model": "mrp.workcenter",
    "type": "ir.actions.act_window",
    "target": "current",
}


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    production_line_ids = fields.One2many(
        "mrp.production.workcenter.line",
        "workcenter_id",
        domain=[("state", "not in", STATIC_STATES)],
        string="Work Orders",
    )

    def _get_workcenter_line_domain(self):
        return [
            ("state", "not in", STATIC_STATES),
            ("workcenter_id", "in", self.ids),
        ]

    def button_workcenter_line(self):
        self.ensure_one()
        domain = self._get_workcenter_line_domain()
        return {
            "view_mode": "tree,form",
            "name": "'%s' Operations" % self.name,
            "res_model": "mrp.production.workcenter.line",
            "type": "ir.actions.act_window",
            "domain": domain,
            "target": "current",
        }
