# Copyright (C) 2017 Akretion (http://www.akretion.com). All Rights Reserved
# @author Florian DA COSTA <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_is_zero


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.depends(
        "move_raw_ids.state",
        "move_raw_ids.quantity",
        "move_finished_ids.state",
        "workorder_ids.state",
        "product_qty",
        "qty_producing",
        "date_start",
    )
    def _compute_state(self):
        super()._compute_state()
        for production in self:
            ctx = dict(production.env.context)
            if ctx.get("previous_state") == "confirmed" and production.date_start:
                production.state = "progress"
            elif (
                ctx.get("previous_state") == "progress"
                and production.product_uom_id
                and float_is_zero(
                    production.qty_producing,
                    precision_rounding=production.product_uom_id.rounding,
                )
            ):
                production.state = "confirmed"
        return

    def action_start(self):
        super().action_start()
        self.write(
            {
                "date_start": fields.Datetime.now(),
            }
        )
        return

    def action_unstart(self):
        self.with_context(previous_state=self.state).qty_producing = 0
        return True
