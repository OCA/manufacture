# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import fields, models


class PurchaseReturnOrderLine(models.Model):
    _inherit = "purchase.return.order.line"

    repair_line_ids = fields.Many2many(comodel_name="repair.line", copy=False)
    repair_fee_ids = fields.Many2many(comodel_name="repair.fee", copy=False)
