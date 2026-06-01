# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    byproduct_auto_pick = fields.Boolean(
        string="Auto-pick Manually Edited Byproducts",
        compute="_compute_byproduct_auto_pick",
        store=True,
        readonly=False,
        help="Keep manually entered byproduct quantities on manufacturing "
        "orders instead of resetting them to the quantity to produce.",
    )

    @api.depends("company_id")
    def _compute_byproduct_auto_pick(self):
        for production in self:
            production.byproduct_auto_pick = production.company_id.byproduct_auto_pick
