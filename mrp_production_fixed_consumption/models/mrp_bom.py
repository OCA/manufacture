# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    fixed_consumption = fields.Boolean(
        help="Consume the component quantities planned on the manufacturing "
        "order even when the produced quantity is lower: the material issued "
        "for the planned quantity is consumed in full and the yield loss is "
        "not pushed back to the components. Not meant for orders closed with "
        "a backorder.",
    )
