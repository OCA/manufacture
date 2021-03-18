# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _check_backorder(self):
        """On the moment of the picking validation, we'll check wether there
        are kits that can't be partially delivered or not"""
        moves = self.mapped("move_lines").filtered(
            lambda x: not x.allow_partial_kit_delivery and x.bom_line_id
        )
        boms = moves.mapped("bom_line_id.bom_id")
        for bom in boms:
            bom_moves = moves.filtered(lambda x: x.bom_line_id.bom_id == bom)
            # We can put it in backorder if the whole kit goes
            if not sum(bom_moves.mapped("quantity_done")):
                continue
            if bom_moves._check_backorder_moves():
                raise ValidationError(
                    _(
                        "You can't make a partial delivery of components of the "
                        "%s kit" % bom.product_tmpl_id.display_name
                    )
                )
        return super()._check_backorder()
