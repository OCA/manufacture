# Copyright (C) 2017 Akretion (http://www.akretion.com). All Rights Reserved
# @author Florian DA COSTA <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.depends(
        "move_raw_ids.state",
        "move_raw_ids.quantity",
        "move_raw_ids.picked",
        "move_finished_ids.state",
        "workorder_ids.state",
        "product_qty",
        "qty_producing",
        "date_start",
    )
    def _compute_state(self):
        res = super()._compute_state()
        for production in self:
            previous_state = production.env.context.get("previous_state")
            if previous_state == "confirmed" and production.date_start:
                production.state = "progress"
            elif (
                previous_state == "progress"
                and production.product_uom_id
                and production.product_uom_id.is_zero(production.qty_producing)
            ):
                production.state = "confirmed"
        return res

    def action_start(self):
        self.ensure_one()
        production = self.with_context(previous_state=self.state)
        res = super(MrpProduction, production).action_start()
        production.write({"date_start": fields.Datetime.now()})
        return res

    def action_unstart(self):
        self.with_context(previous_state=self.state).qty_producing = 0
        return True
