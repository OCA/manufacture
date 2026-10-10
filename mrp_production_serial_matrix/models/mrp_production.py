# Copyright 2021 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    show_serial_matrix = fields.Boolean(compute="_compute_show_serial_matrix")

    def _compute_show_serial_matrix(self):
        for rec in self:
            rec.show_serial_matrix = rec.product_id.tracking == "serial"
