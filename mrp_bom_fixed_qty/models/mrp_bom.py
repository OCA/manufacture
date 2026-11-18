# Copyright 2026 Dixmit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    fixed_qty = fields.Float(
        help="If set, this component is consumed in the quantity of the line "
        "on every manufacturing order, regardless of the quantity produced.",
    )


class MrpBomByproduct(models.Model):
    _inherit = "mrp.bom.byproduct"

    fixed_qty = fields.Float(
        help="If set, this by-product is produced in the quantity of the line "
        "on every manufacturing order, regardless of the quantity produced.",
    )
