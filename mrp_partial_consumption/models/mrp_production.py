# Copyright 2023 Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def button_partial_consumption(self):
        self.ensure_one()
        to_consume = self.move_raw_ids.move_line_ids.filtered(
            lambda x: x.state not in ("done", "cancel") and x.qty_done > 0
        )
        to_consume.mapped("move_id")._action_done()
