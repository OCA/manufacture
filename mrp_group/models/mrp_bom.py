from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"
    
    mrp_group_ids = fields.Many2many(
        "mrp.group", string="MRP Groups"
    ) 
    