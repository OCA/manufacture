# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    mo_grouping_max_hour = fields.Integer(
        string="MO grouping max. hour (UTC)",
        help="The maximum hour (between 0 and 23) for considering new "
        "manufacturing orders inside the same interval period, and thus "
        "being grouped on the same MO. IMPORTANT: The hour should be "
        "expressed in UTC.",
        default=19,
    )
    mo_grouping_interval = fields.Integer(
        string="MO grouping interval (days)",
        help="The number of days for grouping together on the same "
        "manufacturing order.",
        default=1,
    )

    @api.constrains("mo_grouping_max_hour")
    def _check_mo_grouping_max_hour(self):
        if self.mo_grouping_max_hour < 0 or self.mo_grouping_max_hour > 23:
            raise exceptions.ValidationError(
                _("You have to enter a valid hour between 0 and 23.")
            )

    @api.constrains("mo_grouping_interval")
    def _check_mo_grouping_interval(self):
        if self.mo_grouping_interval < 0:
            raise exceptions.ValidationError(
                _("You have to enter a positive value for interval.")
            )
