# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    package_propagation = fields.Boolean(
        default=False,
        help=(
            "Allow to propagate the package "
            "from a component to the finished product."
        ),
    )
    display_package_propagation = fields.Boolean(
        compute="_compute_display_package_propagation"
    )

    @api.depends(
        "type",
        "product_tmpl_id.tracking",
        "product_qty",
        "product_uom_id",
        "bom_line_ids.product_id.tracking",
        "bom_line_ids.product_qty",
        "bom_line_ids.product_uom_id",
    )
    def _compute_display_package_propagation(self):
        """Check if a package can be propagated.

        A package can be propagated from a component to the finished product if
        the type of the BoM is normal (Manufacture this product)
        """
        for bom in self:
            bom.display_package_propagation = (
                bom.type in self._get_package_propagation_bom_types()
            )

    def _get_package_propagation_bom_types(self):
        return ["normal"]

    @api.onchange("display_package_propagation")
    def onchange_display_package_propagation(self):
        if not self.display_package_propagation:
            self.package_propagation = False

    @api.constrains("package_propagation")
    def _check_propagate_package(self):
        for bom in self:
            if not bom.package_propagation:
                continue
            if not bom.bom_line_ids.filtered("propagate_package"):
                raise ValidationError(
                    _(
                        "With 'Package Propagation' enabled, a line has "
                        "to be configured with the 'Propagate Package' option."
                    )
                )
