# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    propagate_package = fields.Boolean(
        default=False,
    )
    display_propagate_package = fields.Boolean(
        compute="_compute_display_propagate_package"
    )

    @api.depends(
        "bom_id.display_package_propagation",
        "bom_id.package_propagation",
    )
    def _compute_display_propagate_package(self):
        for line in self:
            line.display_propagate_package = (
                line.bom_id.display_package_propagation
                and line.bom_id.package_propagation
            )

    @api.constrains("propagate_package")
    def _check_propagate_package(self):
        """
        This function should check:

        - if the bom has package_propagation marked, there is one and
          only one line of this bom with `propagate_package` marked.
        - if the component qty is 1 unit
        """
        uom_unit = self.env.ref("uom.product_uom_unit")
        for line in self:
            if not line.bom_id.package_propagation:
                continue
            lines_to_propagate = line.bom_id.bom_line_ids.filtered(
                lambda o: o.propagate_package
            )
            if len(lines_to_propagate) > 1:
                raise ValidationError(
                    _(
                        "Only one component can propagate its package "
                        "to the finished product."
                    )
                )
            qty_ok = (
                tools.float_compare(
                    line.product_qty, 1, precision_rounding=uom_unit.rounding
                )
                == 0
            )
            if line.propagate_package and (
                line.product_uom_id != uom_unit or not qty_ok
            ):
                raise ValidationError(
                    _("The component propagating the package must consume 1 %s.")
                    % uom_unit.display_name
                )
