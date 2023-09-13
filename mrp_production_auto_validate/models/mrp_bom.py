# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    mo_auto_validation = fields.Boolean(
        string="Order Auto Validation",
        help=(
            "Validate automatically the manufacturing order "
            "when the 'Pick Components' transfer is validated.\n"
            "This behavior is available only if the warehouse is configured "
            "with 2 or 3 steps."
        ),
        default=False,
    )
    mo_auto_validation_warning = fields.Char(
        string="Order Auto Validation (warning)",
        compute="_compute_mo_auto_validation_warning",
    )

    @api.onchange("type")
    def onchange_type_auto_validation(self):
        if self.type != "normal":
            self.mo_auto_validation = self.mo_auto_validation_warning = False

    @api.depends("mo_auto_validation")
    def _compute_mo_auto_validation_warning(self):
        for bom in self:
            bom.mo_auto_validation_warning = False
            if bom.mo_auto_validation:
                bom.mo_auto_validation_warning = _(
                    "The Quantity To Produce of an order is now "
                    "restricted to the BoM Quantity."
                )
