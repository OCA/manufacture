from odoo import api, models

from odoo.addons.base_exception.exceptions import BaseExceptionError


class MrpProduction(models.Model):
    _name = "mrp.production"
    _inherit = ["mrp.production", "base.exception"]

    def button_mark_done(self):
        try:
            has_exceptions = self.detect_exceptions()
        except BaseExceptionError:
            has_exceptions = True
        if has_exceptions and not self.ignore_exception:
            return self._popup_exceptions()
        return super().button_mark_done()

    @api.model
    def _get_popup_action(self):
        return self.env.ref("mrp_exception.action_mrp_exception_confirm")
