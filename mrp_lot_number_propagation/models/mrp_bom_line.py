# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    propagate_lot_number = fields.Boolean(
        default=False,
    )
    display_propagate_lot_number = fields.Boolean(
        compute="_compute_display_propagate_lot_number"
    )

    @api.depends(
        "bom_id.display_lot_number_propagation",
        "bom_id.lot_number_propagation",
    )
    def _compute_display_propagate_lot_number(self):
        for line in self:
            line.display_propagate_lot_number = (
                line.bom_id.display_lot_number_propagation
                and line.bom_id.lot_number_propagation
            )

    @api.constrains(
        "propagate_lot_number",
        "bom_id.lot_number_propagation",
        "product_id.tracking",
        "bom_id.product_tmpl_id.tracking",
    )
    def _check_propagate_lot_number(self):
        """
        This function should check:

        - if the bom has lot_number_propagation marked, there is one and
          only one line of this bom with propagate_lot_number marked.
        - the bom line being marked with lot_number_propagation is of the same
          tracking type as the finished product
        """
        for line in self:
            lines_to_propagate = line.bom_id.bom_line_ids.filtered(
                lambda o: o.propagate_lot_number
            )
            if line.bom_id.lot_number_propagation:
                if len(lines_to_propagate) > 1:
                    raise ValidationError(
                        _(
                            "Only one BoM line can propagate its lot/serial number "
                            "to the finished product."
                        )
                    )
                if line.propagate_lot_number and line.product_id.tracking != "serial":
                    raise ValidationError(
                        _(
                            "Only components tracked by serial number can propagate "
                            "its lot/serial number to the finished product."
                        )
                    )
