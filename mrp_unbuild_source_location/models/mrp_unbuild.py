# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    location_domain = fields.Binary(compute="_compute_location_domain")

    @api.depends("lot_id", "product_id", "company_id")
    def _compute_location_domain(self):
        for record in self:
            domain = [
                ("usage", "in", ["internal", "transit"]),
                "|",
                ("company_id", "=", False),
                ("company_id", "=", record.company_id.id),
            ]
            if record.product_id:
                quant_domain = [
                    ("product_id", "=", record.product_id.id),
                    ("quantity", ">", 0),
                ]
                if record.lot_id:
                    quant_domain.append(("lot_id", "=", record.lot_id.id))
                quants = self.env["stock.quant"].search(quant_domain)
                location_ids = quants.location_id.ids
                domain = expression.AND([domain, [("id", "in", location_ids)]])
            record.location_domain = domain

    @api.depends("company_id", "location_domain")
    def _compute_location_id(self):
        super()._compute_location_id()
        for record in self:
            locations = self.env["stock.location"].search(record.location_domain)
            if len(locations) == 1:
                record.location_id = locations
        return

    @api.constrains("lot_id")
    def _check_lot_location(self):
        for record in self:
            if not record.lot_id:
                continue
            if not self.env["stock.location"].search(record.location_domain, limit=1):
                raise ValidationError(_("No location with positive stock found."))
