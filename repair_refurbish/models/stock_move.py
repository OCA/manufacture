# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class StockMove(models.Model):

    _inherit = "stock.move"

    @api.model_create_multi
    def create(self, vals_list):
        if "to_refurbish" in self.env.context and self.env.context["to_refurbish"]:
            if "force_refurbish_location_dest_id" in self.env.context:
                for vals in vals_list:
                    vals["location_dest_id"] = self.env.context[
                        "force_refurbish_location_dest_id"
                    ]
        return super().create(vals_list)


class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        if "to_refurbish" in self.env.context and self.env.context["to_refurbish"]:
            if "force_refurbish_location_dest_id" in self.env.context:
                for vals in vals_list:
                    vals["location_dest_id"] = self.env.context[
                        "force_refurbish_location_dest_id"
                    ]
        return super().create(vals_list)
