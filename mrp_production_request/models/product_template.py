# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    mrp_production_request = fields.Boolean(
        string="Manufacturing Request",
        help="Check this box to generate manufacturing request instead of "
        "generating manufacturing orders from procurement.",
    )

    mrp_production_request_ids = fields.One2many(
        comodel_name="mrp.production.request",
        inverse_name="product_tmpl_id",
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
