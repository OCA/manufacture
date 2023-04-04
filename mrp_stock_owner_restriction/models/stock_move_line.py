# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _action_done(self):
        for line in self:
            owner = line.move_id.production_id.owner_id
            if owner:
                line.move_id.write({"restrict_partner_id": owner.id})
                line.write({"owner_id": owner.id})
        return super()._action_done()
