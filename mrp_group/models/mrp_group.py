from odoo import api, fields, models, _
from random import randint



class MrpGroup(models.Model):
    _name = "mrp.group"
    _rec_name = 'name'
    _inherit = ['mail.thread']
    _description = "Mrp Group"
    
    def _get_default_color(self):
        return randint(1, 11)
    
    name = fields.Char(string='Name',tracking=True)
    color = fields.Integer(string='Color', default=_get_default_color)
    
    
    _sql_constraints=[('unique_name','unique(name)','Group name should be unique!' )]
    