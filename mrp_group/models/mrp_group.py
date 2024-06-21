from odoo import fields, models 
from random import randint


class MrpGroup(models.Model):
    _name = "mrp.group"
    _rec_name = "name"
    _inherit = ["mail.thread"]
    _description = "Mrp Group"
    
    def _get_default_color(self):
        return randint(1, 11)
    
    name = fields.Char(tracking=True)
    color = fields.Integer(default=_get_default_color)
    
    _sql_constraints = [("unique_name", "unique(name)", "Group name should be unique!")]
