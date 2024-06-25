from odoo import fields, models


class MrpGroup(models.Model):
    _name = "mrp.group"
    _rec_name = "name"
    _inherit = ["mail.thread"]
    _description = "Mrp Group"

    name = fields.Char(tracking=True)
    color = fields.Integer()

    _sql_constraints = [("unique_name", "unique(name)", "Group name should be unique!")]
