# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    pending_order_ids = fields.One2many(
        "mrp.workorder",
        "workcenter_id",
        domain=[("state", "in", ("pending", "ready", "progress"))],
        string="Work Orders",
    )

    def _get_workcenter_line_domain(self):
        return [
            ("state", "in", ("pending", "ready", "progress")),
            ("workcenter_id", "in", self.ids),
        ]

    def button_workcenter_line(self):
        self.ensure_one()
        domain = self._get_workcenter_line_domain()
        return {
            "view_mode": "tree,form",
            "name": "'%s' Workorders" % self.name,
            "res_model": "mrp.workorder",
            "type": "ir.actions.act_window",
            "domain": domain,
            "target": "current",
        }
