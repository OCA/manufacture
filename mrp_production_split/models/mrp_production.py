# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def copy_data(self, default=None):
        # OVERRIDE copy the date_planned_start and date_planned_end when splitting
        # productions, as they are not copied by default (copy=False).
        [data] = super().copy_data(default=default)
        data.setdefault("date_planned_start", self.date_planned_start)
        data.setdefault("date_planned_finished", self.date_planned_finished)
        return [data]

    def action_split(self):
        self.ensure_one()
        self._check_company()
        if self.state in ("draft", "done", "to_close", "cancel"):
            raise UserError(
                _(
                    "Cannot split a manufacturing order that is in '%s' state.",
                    self._fields["state"].convert_to_export(self.state, self),
                )
            )
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mrp_production_split.action_mrp_production_split_wizard"
        )
        action["context"] = {"default_production_id": self.id}
        return action
