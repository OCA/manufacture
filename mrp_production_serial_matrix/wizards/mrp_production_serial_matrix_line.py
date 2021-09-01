# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpProductionSerialMatrix(models.TransientModel):
    _name = "mrp.production.serial.matrix.line"
    _description = "Mrp Production Serial Matrix Line"

    wizard_id = fields.Many2one(
        comodel_name="mrp.production.serial.matrix",
    )
    production_id = fields.Many2one(related="wizard_id.production_id")
    component_id = fields.Many2one(comodel_name="product.product")
    component_column_name = fields.Char()
    finished_lot_id = fields.Many2one(comodel_name="stock.production.lot")
    finished_lot_name = fields.Char()
    component_lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        domain="[('id', 'in', allowed_component_lot_ids)]",
    )
    allowed_component_lot_ids = fields.Many2many(
        comodel_name="stock.production.lot",
        compute="_compute_allowed_component_lot_ids",
    )
    lot_qty = fields.Float(digits="Product Unit of Measure")

    def _compute_allowed_component_lot_ids(self):
        for rec in self:
            available_quants = self.env["stock.quant"].search(
                [
                    ("location_id", "child_of", rec.production_id.location_src_id.id),
                    ("product_id", "=", rec.component_id.id),
                    ("quantity", ">", 0),
                ]
            )
            rec.allowed_component_lot_ids = available_quants.mapped("lot_id")
