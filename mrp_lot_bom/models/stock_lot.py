# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    production_ids = fields.One2many(
        comodel_name="mrp.production",
        inverse_name="lot_producing_id",
        string="Manufacturing Orders",
    )
    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="Bill of Materials",
        compute="_compute_bom_id",
        store=True,
        index=True,
        help="Bill of Materials of the last done manufacturing order that "
        "produced this lot/serial number.",
    )

    @api.depends(
        "production_ids.state",
        "production_ids.bom_id",
        "production_ids.date_finished",
    )
    def _compute_bom_id(self):
        for lot in self:
            productions = lot.production_ids.filtered(
                lambda p: p.state == "done"
            ).sorted(lambda p: (p.date_finished or p.create_date, p.id), reverse=True)
            lot.bom_id = fields.first(productions).bom_id
