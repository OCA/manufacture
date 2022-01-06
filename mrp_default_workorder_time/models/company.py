# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    use_projected_time_work_orders = fields.Boolean(
        string="Use projected time work orders?",
        default=True,
    )
    minimum_order_time_threshold = fields.Float(
        string="Minimum order time threshold(%)",
        required=False,
        default=10,
    )
    maximum_order_time_threshold = fields.Float(
        string="Maximum order time threshold(%)",
        required=False,
        default=150,
    )
