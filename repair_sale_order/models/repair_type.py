# Copyright 2022 ForgeFlow S.L. (https://forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class RepairType(models.Model):

    _inherit = "repair.type"

    create_sale_order = fields.Boolean(
        string="Create sale order?",
        default=False,
    )
