# © 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from odoo import api, models


class ReportBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    @api.model
    def get_html(self, bom_id=False, searchQty=1, searchVariant=False):
        """Set quantity from stored parameter"""
        IConf = self.env["ir.config_parameter"].sudo()
        param = IConf.get_param("request_bom_structure")
        param = json.loads(param)
        if self.env.context.get("model") == "mrp.production.request" and searchQty == 1:
            # We don't want used stored quantity when we are in an other situation
            # to avoid break native behavior
            searchQty = param.get(str(self.env.context.get("uid"))) or searchQty
        return super().get_html(
            bom_id=bom_id, searchQty=searchQty, searchVariant=searchVariant
        )
