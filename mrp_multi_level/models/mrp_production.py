# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# - Héctor Villarreal <hector.villarreal@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class MrpProduction(models.Model):
    """Manufacturing Orders"""

    _inherit = "mrp.production"

    planned_order_id = fields.Many2one(comodel_name="mrp.planned.order")
