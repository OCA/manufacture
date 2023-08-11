from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    variable = fields.Boolean(help="Used as configurable process for product")
