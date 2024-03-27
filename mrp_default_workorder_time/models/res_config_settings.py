# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    use_projected_time_work_orders = fields.Boolean(
        related="company_id.use_projected_time_work_orders", readonly=False
    )
    minimum_order_time_threshold = fields.Float(
        related="company_id.minimum_order_time_threshold", readonly=False
    )
    maximum_order_time_threshold = fields.Float(
        related="company_id.maximum_order_time_threshold", readonly=False
    )
