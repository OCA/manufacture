# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _post_inventory(self, cancel_backorder=False):
        res = super()._post_inventory(cancel_backorder=cancel_backorder)
        for order in self:
            if order.lot_producing_id and not order.lot_producing_id.production_date:
                order.lot_producing_id.production_date = fields.Datetime.now()
        return res
