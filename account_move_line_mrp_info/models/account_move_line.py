# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    mrp_production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Manufacturing Order",
        index="btree_not_null",
        readonly=True,
    )
    unbuild_id = fields.Many2one(
        comodel_name="mrp.unbuild",
        string="Unbuild Order",
        index="btree_not_null",
        readonly=True,
    )
    # O2M from the Odoo standard M2O
    mrp_workcenter_productivity_ids = fields.One2many(
        comodel_name="mrp.workcenter.productivity",
        inverse_name="account_move_line_id",
    )
