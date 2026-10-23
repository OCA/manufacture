# Copyright (C) 2017 Akretion (http://www.akretion.com). All Rights Reserved
# @author Florian DA COSTA <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    date_started = fields.Datetime(
        string="Started On",
        compute="_compute_date_started",
        store=True,
        copy=False,
    )

    @api.depends("state")
    def _compute_date_started(self):
        for production in self:
            date_started = production.date_started
            if production.state in ("draft", "confirmed"):
                date_started = False
            elif not date_started and production.state != "cancel":
                date_started = fields.Datetime.now()
            production.date_started = date_started

    def _check_can_unstart(self):
        for production in self:
            if production.state != "progress":
                raise UserError(
                    self.env._(
                        "Only manufacturing orders in progress can be unstarted: %s.",
                        production.display_name,
                    )
                )
            if production.qty_producing:
                raise UserError(
                    self.env._(
                        "You cannot unstart %s because a quantity is already "
                        "being produced.",
                        production.display_name,
                    )
                )
            if production.workorder_ids.filtered(
                lambda wo: wo.state in ("progress", "done")
            ):
                raise UserError(
                    self.env._(
                        "You cannot unstart %s because some work orders are "
                        "started or done.",
                        production.display_name,
                    )
                )
            if production.move_raw_ids.filtered("picked"):
                raise UserError(
                    self.env._(
                        "You cannot unstart %s because some components are "
                        "already picked.",
                        production.display_name,
                    )
                )

    def action_unstart(self):
        self._check_can_unstart()
        self.write({"state": "confirmed"})
        return True
