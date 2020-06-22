# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    mo_type_id = fields.Many2one(
        comodel_name="manufacturing.order.type", string="Manufacturing Order Type",
    )


class ProductTemplate(models.Model):
    _inherit = "product.template"

    mo_type_id = fields.Many2one(
        comodel_name="manufacturing.order.type", string="Manufacturing Order Type",
    )
