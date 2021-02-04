# © 2016 Akretion (http://www.akretion.com)
# David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.web.controllers import main


class Action(main.Action):
    @http.route("/web/action/load", type="json", auth="user")
    def load(self, action_id, do_not_eval=False, additional_context=None):
        if "mrp_load" in request.env.registry._init_modules:
            env = request.env
            try:
                action_id = int(action_id)
                mrp_action_id = env.ref("mrp.mrp_workcenter_action").id
                if action_id == mrp_action_id:
                    env["mrp.workcenter"].auto_recompute_load()
            except ValueError:
                if action_id == "mrp.mrp_workcenter_action":
                    env["mrp.workcenter"].auto_recompute_load()
                raise
        return super().load(
            action_id, do_not_eval=do_not_eval, additional_context=additional_context
        )
