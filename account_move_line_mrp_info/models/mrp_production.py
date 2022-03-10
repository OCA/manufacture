# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    account_move_line_ids = fields.One2many(
        comodel_name="account.move.line", inverse_name="mrp_production_id", copy=False
    )


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    account_move_line_ids = fields.One2many(
        comodel_name="account.move.line", inverse_name="unbuild_id", copy=False
    )
