# Copyright 2023 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    primecontractor_raw_material = fields.Boolean(
        "Primecontractor Raw Material",
        help="Define if this material comes from the prime contractor",
        default=False,
    )
