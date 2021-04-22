# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# Copyright 2016-21 ForgeFlow S.L. (https://www.forgeflow.com)
# - Jordi Ballester Alomar <jordi.ballester@forgeflow.com>
# - Lois Rilo Antelo <lois.rilo@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MrpArea(models.Model):
    _name = "mrp.area"
    _description = "MRP Area"

    name = fields.Char(required=True)
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse", string="Warehouse", required=True
    )
    company_id = fields.Many2one(
        comodel_name="res.company", related="warehouse_id.company_id", store=True
    )
    location_id = fields.Many2one(
        comodel_name="stock.location", string="Location", required=True
    )
    active = fields.Boolean(default=True)
    calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Working Hours",
        related="warehouse_id.calendar_id",
    )

    @api.model
    def _datetime_to_date_tz(self, dt_to_convert=None):
        """Coverts a datetime to date considering the timezone of MRP Area.
        If no datetime is provided, it returns today's date in the timezone."""
        return fields.Date.context_today(
            self.with_context(tz=self.calendar_id.tz),
            timestamp=dt_to_convert,
        )

    def _get_locations(self):
        self.ensure_one()
        return self.env["stock.location"].search(
            [("id", "child_of", self.location_id.id)]
        )
