# © 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from odoo import _, models


class MrpProductionRequest(models.Model):
    _inherit = "mrp.production.request"

    def button_open_structure_report(self):
        """ - store quantity in parameter
            - return action client
        """
        self.ensure_one()
        IConf = self.env["ir.config_parameter"].sudo()
        try:
            param = json.loads(IConf.get_param("request_bom_structure")) or {}
        except Exception:
            param = {}
        param[str(self.env.context.get("uid"))] = self.product_qty
        # bom structure report'll use this stored param
        IConf.set_param("request_bom_structure", json.dumps(param))
        return {
            "name": _("Structure"),
            "res_model": "report.mrp.report_bom_structure",
            "context": {
                "model": "report.mrp.report_bom_structure",
                "active_id": self.bom_id.id,
            },
            "target": "current",
            "tag": "mrp_bom_report",
            "type": "ir.actions.client",
        }
