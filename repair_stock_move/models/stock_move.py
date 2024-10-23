# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    repair_line_id = fields.Many2one(
        comodel_name="repair.line",
        string="Repair Line",
        ondelete="cascade",
    )

    def _get_available_quantity(
        self,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
        allow_negative=False,
    ):
        if self.repair_line_id and self.repair_line_id.lot_id:
            lot_id = self.repair_line_id.lot_id

        return super()._get_available_quantity(
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
            allow_negative=allow_negative,
        )

    def _update_reserved_quantity(
        self,
        need,
        available_quantity,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        if self.repair_line_id and self.repair_line_id.lot_id:
            lot_id = self.repair_line_id.lot_id
        return super(StockMove, self)._update_reserved_quantity(
            need,
            available_quantity,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(
            quantity=quantity, reserved_quant=reserved_quant
        )
        if self.repair_line_id and self.repair_line_id.lot_id:
            vals["lot_id"] = self.repair_line_id.lot_id.id
        return vals
