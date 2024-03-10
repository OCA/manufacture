from odoo import fields, models


class BomLineDescription(models.Model):
    _name = "bom.line.description"
    _description = "Bom line description"

    name = fields.Char(required=True)
    description = fields.Char(help=" alternative name used for commercial purpose")
