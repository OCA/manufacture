# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _post_inventory(self, cancel_backorder=False):
        for move in self.move_raw_ids:
            if move.product_id.skip_mo_consumption:
                # Mark the move as done now, so that the inventory is not impacted
                move.write({"state": "done", "date": fields.Datetime.now()})
        return super()._post_inventory(cancel_backorder)
