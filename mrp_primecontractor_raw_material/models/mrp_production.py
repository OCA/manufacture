# Copyright 2023 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_primecontractor_location_src_id(self):
        self.ensure_one()
        warehouse = self.picking_type_id.warehouse_id
        return self.env["stock.location"].search(
            [
                (
                    "location_id",
                    "child_of",
                    warehouse.primecontractor_view_location_id.id,
                ),
                ("primecontractor_id", "=", self.partner_id.id),
            ]
        )

    def _get_move_raw_values(
        self,
        product_id,
        product_uom_qty,
        product_uom,
        operation_id=False,
        bom_line=False,
    ):
        res = super()._get_move_raw_values(
            product_id, product_uom_qty, product_uom, operation_id, bom_line
        )
        if bom_line and bom_line.primecontractor_raw_material:
            location = self._get_primecontractor_location_src_id()
            if not location:
                raise UserError(
                    _(
                        "You must have a prime contractor source location "
                        "for this customer since you have defined a prime "
                        "contractor raw material in your BOM."
                    )
                )
            res.update({"location_id": location.id})
        return res
