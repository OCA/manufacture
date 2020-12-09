# Copyright 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    qty_by_workcenter_ids = fields.One2many(
        comodel_name="product.workcenter.quantity",
        inverse_name="product_id",
        groups="mrp_production_request.group_mrp_production_request_user",
        string="Capacity by workcenter",
    )
