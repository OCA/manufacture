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

    @api.constrains("propagate_lot_number")
    def _check_propagate_lot_number(self):
        """
        This function should check:

        - if the bom has lot_number_propagation marked, there is one and
          only one line of this bom with propagate_lot_number marked.
        - the bom line being marked with lot_number_propagation is of the same
          tracking type as the finished product
        """
        for line in self:
            if not line.bom_id.lot_number_propagation:
                continue
            
            # Check if component supports lot number propagation
            # Support both traditional product_id and component_template_id approaches
            product_tracking = False
            if line.product_id:
                product_tracking = line.product_id.tracking
            elif line.component_template_id:
                # For component_template_id, check if any variant has serial tracking
                variants = line.component_template_id.product_variant_ids
                if variants:
                    # Check if all variants have the same tracking type
                    tracking_types = variants.mapped('tracking')
                    if len(set(tracking_types)) == 1:
                        product_tracking = tracking_types[0]
                    else:
                        # Variants have different tracking types, cannot propagate
                        product_tracking = None
            
            if line.propagate_lot_number and product_tracking != "serial":
                raise ValidationError(
                    _(
                        "Only components tracked by serial number can propagate "
                        "its lot/serial number to the finished product."
                    )
                )