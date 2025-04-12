# Copyright 2023 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    owner_id = fields.Many2one(
        "res.partner",
        "Assign Owner",
        readonly=True,
        check_company=True,
        help="Produced products will be assigned to this owner.",
    )
    owner_restriction = fields.Selection(related="picking_type_id.owner_restriction")

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to ensure owner_id is set correctly."""
        records = super().create(vals_list)
        for record in records:
            if (
                record.picking_type_id
                and record.picking_type_id.owner_restriction == "unassigned_owner"
                and not record.owner_id
            ):
                record.owner_id = self.env.company.partner_id
        return records

    def write(self, vals):
        if "owner_id" in vals:
            for production in self:
                if production.owner_restriction in (
                    "unassigned_owner",
                    "picking_partner",
                ):
                    production.move_line_raw_ids.unlink()
        return super().write(vals)
