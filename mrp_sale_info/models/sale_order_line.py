# Copyright 2021 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    production_ids = fields.Many2many(
        comodel_name="mrp.production",
        relation="sale_line_production_rel",
        column1="line_id",
        column2="production_id",
        string="Manufacturing orders",
    )
