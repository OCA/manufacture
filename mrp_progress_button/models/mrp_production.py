# Copyright (C) 2017 Akretion (http://www.akretion.com). All Rights Reserved
# @author Florian DA COSTA <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.depends(
        "move_raw_ids.state",
        "move_raw_ids.quantity_done",
        "move_finished_ids.state",
        "workorder_ids.state",
        "product_qty",
        "qty_producing",
        "date_start",
    )
    def _compute_state(self):
        res = super()._compute_state()
        for production in self:
            if production.state == "confirmed" and production.date_start:
                production.state = "progress"
        return res

    def action_progress(self):
        self.write(
            {
                "date_start": datetime.now(),
            }
        )
        return True

    def action_unstart(self):
        self.write({"state": "confirmed", "date_start": False, "qty_producing": 0})
        return True
