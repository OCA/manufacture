# Copyright 2023 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    group_id = fields.Many2one(
        compute="_compute_group_id",
        readonly=False,
    )

    @api.depends("location_id")
    def _compute_group_id(self):
        for orderpoint in self:
            if orderpoint.location_id and orderpoint.location_id.primecontractor_id:
                orderpoint.group_id = (
                    orderpoint.location_id.primecontractor_procurement_group_id
                )
