# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    valuation_clear_account_id = fields.Many2one(
        "account.account",
        "Manufacturing Clearing Account",
        domain=[("internal_type", "=", "other"), ("deprecated", "=", False)],
        help="Used to clear the WIP accounts, the balance is posted to the variance account",
    )
    valuation_variance_account_id = fields.Many2one(
        "account.account",
        "Manufacturing Variance Account",
        domain=[("internal_type", "=", "other"), ("deprecated", "=", False)],
        help="Used to post variances versus planned, when closing a Manufacturing Order",
    )
