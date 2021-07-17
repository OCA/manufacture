# Copyright 2004-2021 Odoo SA for function _set_qty_producing
# Copyright 2021 Le Filament
# License GPL-3.0 or later (https://www.gnu.org/licenses/gpl.html).

from odoo import fields, models
from odoo.tools import float_round


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    create_multi = fields.Boolean("Generate serial numbers")
    generated_serials_ids = fields.One2many(
        "stock.production.lot",
        "production_id",
        "Serial Numbers",
        copy=True,
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
    )
    generated_serials = fields.Integer("Qty of generated SN", default=0)

    def action_generate_serials(self):
        self.ensure_one()
        if self.generated_serials < self.product_qty:
            for item in range(self.generated_serials, int(self.product_qty)):
                lot_sequence_id = self.product_tmpl_id.lot_sequence_id
                next_lot_number = lot_sequence_id._next()
                self.env["stock.production.lot"].create(
                    {
                        "product_id": self.product_id.id,
                        "company_id": self.company_id.id,
                        "production_id": self.id,
                        "name": next_lot_number,
                    }
                )
                self.generated_serials = item + 1
            self.qty_producing = self.generated_serials
            lot_ids = self.env["stock.production.lot"].search(
                [
                    ("product_id", "=", self.product_id.id),
                    ("company_id", "=", self.company_id.id),
                    ("production_id", "=", self.id),
                ]
            )
            self.generated_serials_ids = [(6, 0, lot_ids.ids)]
            if self.product_id.tracking == "serial":
                self._set_qty_producing()
                self.move_finished_ids.filtered(
                    lambda m: m.product_id == self.product_id
                ).lot_ids = self.generated_serials_ids

    # This function is copied from Odoo code
    # (https://github.com/odoo/odoo/blob/14.0/addons/mrp/models/mrp_production.py#L934)
    # only extra check add on first if wrt source code
    def _set_qty_producing(self):
        if self.product_id.tracking == "serial" and not self.create_multi:
            qty_producing_uom = self.product_uom_id._compute_quantity(
                self.qty_producing, self.product_id.uom_id, rounding_method="HALF-UP"
            )
            if qty_producing_uom != 1:
                self.qty_producing = self.product_id.uom_id._compute_quantity(
                    1, self.product_uom_id, rounding_method="HALF-UP"
                )

        for move in self.move_raw_ids | self.move_finished_ids.filtered(
            lambda m: m.product_id != self.product_id
        ):
            if move._should_bypass_set_qty_producing() or not move.product_uom:
                continue
            new_qty = float_round(
                (self.qty_producing - self.qty_produced) * move.unit_factor,
                precision_rounding=move.product_uom.rounding,
            )
            move.move_line_ids.filtered(
                lambda ml: ml.state not in ("done", "cancel")
            ).qty_done = 0
            move.move_line_ids = move._set_quantity_done_prepare_vals(new_qty)
