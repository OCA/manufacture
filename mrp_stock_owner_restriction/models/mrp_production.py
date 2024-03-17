# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    owner_id = fields.Many2one(
        "res.partner",
        "Assign Owner",
        readonly=True,
        states={"draft": [("readonly", False)], "confirmed": [("readonly", False)]},
        check_company=True,
        help="Produced products will be assigned to this owner.",
    )
    owner_restriction = fields.Selection(related="picking_type_id.owner_restriction")
