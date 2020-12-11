# Copyright 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class MrpProductionRequestCreateMo(models.TransientModel):
    _inherit = "mrp.production.request.create.mo"

    def _prepare_manufacturing_order(self):
        vals = super()._prepare_manufacturing_order()
        vals["origin"] = "%s %s" % (
            vals.get("origin") or "",
            self.env.context.get("workcenter", ""),
        )
        return vals
