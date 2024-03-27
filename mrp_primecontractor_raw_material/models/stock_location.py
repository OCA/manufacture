# Copyright 2023 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class Location(models.Model):
    _inherit = "stock.location"

    primecontractor_id = fields.Many2one(
        "res.partner",
        "Primecontractor",
        check_company=True,
    )

    primecontractor_raw_material_location = fields.Boolean(
        "Prime Contractor Raw Material Location",
        compute="_compute_primecontractor_raw_material_location",
        store=True,
    )

    primecontractor_procurement_group_id = fields.Many2one(
        "procurement.group", "Prime Contractor Procurement Group", copy=False
    )

    @api.depends("location_id")
    def _compute_primecontractor_raw_material_location(self):
        for location in self:
            location.primecontractor_raw_material_location = bool(
                self.env["stock.warehouse"].search(
                    [
                        (
                            "primecontractor_view_location_id",
                            "parent_of",
                            location.location_id.id,
                        )
                    ],
                    limit=1,
                )
            )

    @api.model
    def _prepare_primecontractor_procurement_group_vals(self, values):
        return {
            "name": values["name"],
            "partner_id": values["primecontractor_id"],
            "move_type": "direct",
        }

    @api.model
    def create(self, values):
        if values.get("primecontractor_id"):
            if not values.get("primecontractor_procurement_group_id"):
                procurement_group_vals = (
                    self._prepare_primecontractor_procurement_group_vals(values)
                )
                values["primecontractor_procurement_group_id"] = (
                    self.env["procurement.group"].create(procurement_group_vals).id
                )

        return super().create(values)
