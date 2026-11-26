# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_show_attachments(self):
        return self.product_id._action_show_attachments()

    def action_show_bom_attachments(self):
        return self.bom_id._action_show_attachments()
