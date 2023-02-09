# © 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    manufacture_order_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Manufacture Order",
        copy=False,
        index=True,
    )

    unbuild_order_id = fields.Many2one(
        comodel_name="mrp.unbuild", string="Unbuild Order", copy=False, index=True
    )
