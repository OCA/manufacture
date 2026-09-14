from odoo import api, models


class MrpProduction(models.Model):
    _inherit = ["mrp.production", "base.exception"]

    def button_mark_done(self):
        if self.detect_exceptions() and not self.ignore_exception:
            return self._popup_exceptions()
        return super().button_mark_done()

    @api.model
    def _get_popup_action(self):
        return self.env.ref("mrp_exception.action_mrp_exception_confirm")