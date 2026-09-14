# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    propagate_lot_profile_id = fields.Many2one(
        comodel_name="mrp.lot.info.propagation.profile",
        compute="_compute_propagate_lot_profile_id",
        inverse="_inverse_propagate_lot_profile_id",
        precompute=True,
        readonly=False,
        store=True,
        string="Lot propagation profile",
    )
    propagate_lot_field_ids = fields.Many2many(
        comodel_name="ir.model.fields",
        related="propagate_lot_profile_id.propagate_lot_field_ids",
        string="Lot fields to propagate",
    )

    @api.depends("product_id", "product_id.categ_id.mrp_propagate_lot_profile_id")
    def _compute_propagate_lot_profile_id(self):
        for line in self:
            line.propagate_lot_profile_id = (
                line.product_id.categ_id.mrp_propagate_lot_profile_id
            )

    def _inverse_propagate_lot_profile_id(self):
        return

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._check_single_propagate_lot_line()
        return lines

    def write(self, vals):
        result = super().write(vals)
        if "product_id" in vals or "propagate_lot_profile_id" in vals:
            self._check_single_propagate_lot_line()
        return result

    @api.constrains("bom_id", "product_id", "propagate_lot_profile_id")
    def _check_single_propagate_lot_line(self):
        for line in self.filtered("propagate_lot_profile_id"):
            if line.product_id.tracking == "none":
                raise ValidationError(
                    self.env._(
                        "Only tracked components can propagate lot information to the "
                        "finished product."
                    )
                )
            other_lines = line.bom_id.bom_line_ids.filtered(
                lambda bom_line, current=line: bom_line != current
                and bom_line.propagate_lot_profile_id
            )
            if other_lines:
                raise ValidationError(
                    self.env._(
                        "Only one BoM line can propagate lot information to the "
                        "finished product."
                    )
                )
