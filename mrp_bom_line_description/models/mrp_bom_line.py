from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"
    description_id = fields.Many2one(comodel_name="bom.line.description")
