# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    display_lots_on_hand_first = fields.Boolean(
        related="picking_type_id.display_lots_on_hand_first"
    )
