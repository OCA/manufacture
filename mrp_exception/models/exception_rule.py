from odoo import fields, models


class ExceptionRule(models.Model):
    _inherit = "exception.rule"

    model = fields.Selection(
        selection_add=[("mrp.production", "Manufacturing Order")],
        ondelete={"mrp.production": "cascade"},
    )
    
    production_ids = fields.Many2many(
        comodel_name="mrp.production",
        relation="mrp_production_exception_rule_rel",
        column1="exception_rule_id",
        column2="production_id",
        string="Manufacturing Orders",
    )