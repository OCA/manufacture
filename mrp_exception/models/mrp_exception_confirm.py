from odoo import fields, models


class MrpExceptionConfirm(models.TransientModel):
    _name = "mrp.exception.confirm"
    _description = "Manufacturing Exception Wizard"
    _inherit = ["exception.rule.confirm"]

    related_model_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Manufacturing Order",
    )
    
    def action_confirm(self):
        self.ensure_one()
        exceptions_blocking = self.exception_ids.filtered("is_blocking")
        
        if self.ignore and not exceptions_blocking:
            self.related_model_id.ignore_exception = True
            # Resume the Odoo MRP completion workflow. 
            # If the MRP workflow yields an intermediate wizard (e.g., backorder),
            # this captures and returns it instead of just closing the exception wizard.
            action = self.related_model_id.button_mark_done()
            if isinstance(action, dict):
                return action
        else:
            self.related_model_id.ignore_exception = False
            
        return super().action_confirm()