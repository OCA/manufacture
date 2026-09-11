# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    mrp_production_request_ids = fields.One2many(
        comodel_name="mrp.production.request",
        inverse_name="product_id",
        string="Manufacturing Requests",
    )

    mrp_production_request_count = fields.Integer(
        string="# Manufacturing Requests",
        compute="_compute_production_request_count",
        store=True,
    )

    @api.depends("mrp_production_request_ids")
    def _compute_production_request_count(self):
        for rec in self:
            rec.mrp_production_request_count = len(rec.mrp_production_request_ids)
