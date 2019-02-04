# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = 'stock.picking.type'

    mrp_no_partial = fields.Boolean(
        string="No Partial Production Orders",
        help="Check this if you want to block production orders if "
             "all the quantities have not been done.",
    )
