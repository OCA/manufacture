# Copyright 2026 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    production_warn_msg = fields.Text(
        string="Production Warning Message", compute="_compute_production_warn_msg"
    )

    @api.depends("bom_id.production_warn")
    def _compute_production_warn_msg(self):
        for rec in self:
            production_warn_msg = False
            if (
                rec.state not in ["done", "cancel"]
                and rec.bom_id
                and rec.bom_id.production_warn == "warning"
            ):
                production_warn_msg = rec.bom_id.production_warn_msg
            rec.production_warn_msg = production_warn_msg

    @api.onchange("bom_id")
    def _onchange_bom_id_warning(self):
        self.ensure_one()
        if self.production_warn_msg:
            return {
                "warning": {
                    "title": _("Warning of MRP BOM"),
                    "message": self.bom_id.production_warn_msg,
                }
            }
