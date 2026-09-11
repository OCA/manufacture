# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import fields, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    propagate_lot_field_ids = fields.Many2many(
        comodel_name="ir.model.fields",
        readonly=True,
        string="Lot fields to propagate",
    )
    propagate_lot_profile_id = fields.Many2one(
        comodel_name="mrp.lot.info.propagation.profile",
        readonly=True,
        string="Lot propagation profile",
    )
    propagate_lot_bom_line_id = fields.Many2one(
        comodel_name="mrp.bom.line",
        readonly=True,
        string="BoM line propagating lot",
    )

    def action_confirm(self):
        res = super().action_confirm()
        self._set_lot_info_propagation_data()
        return res

    def button_mark_done(self):
        self._check_lot_info_propagation()
        self._propagate_lot_info()
        res = super().button_mark_done()
        if not isinstance(res, dict):
            self._propagate_lot_info_to_byproducts()
        return res

    def _set_lot_info_propagation_data(self):
        for production in self:
            bom_line = production.bom_id.bom_line_ids.filtered(
                "propagate_lot_profile_id"
            )
            if len(bom_line) > 1:
                raise UserError(
                    self.env._(
                        "Only one BoM line can propagate lot information to the "
                        "finished product."
                    )
                )
            if bom_line:
                production.propagate_lot_bom_line_id = bom_line
                production.propagate_lot_profile_id = bom_line.propagate_lot_profile_id
                production.propagate_lot_field_ids = (
                    bom_line.propagate_lot_profile_id.propagate_lot_field_ids
                )
            elif not production.bom_id:
                production.propagate_lot_bom_line_id = False
                production.propagate_lot_profile_id = (
                    production.product_id.categ_id.mrp_propagate_lot_profile_id
                )
                production.propagate_lot_field_ids = (
                    production.propagate_lot_profile_id.propagate_lot_field_ids
                )
            else:
                production.propagate_lot_bom_line_id = False
                production.propagate_lot_profile_id = False
                production.propagate_lot_field_ids = False

    def _get_lot_info_propagation_source_lots(self):
        self.ensure_one()
        if self.propagate_lot_bom_line_id:
            source_move = self.move_raw_ids.filtered(
                lambda move: move.bom_line_id == self.propagate_lot_bom_line_id
                and move.state != "cancel"
            )
        else:
            source_move = self.move_raw_ids.filtered(
                lambda move: move.state != "cancel"
            )
        move_lines = source_move.move_line_ids.filtered(
            lambda line: line.lot_id and line.quantity
        )
        return move_lines.lot_id

    def _check_lot_info_propagation(self):
        for production in self.filtered("propagate_lot_field_ids"):
            source_lots = production._get_lot_info_propagation_source_lots()
            if len(source_lots) != 1:
                raise UserError(
                    self.env._(
                        "Lot field propagation requires exactly one consumed lot "
                        "on the configured component."
                    )
                )

    def _propagate_lot_info(self):
        for production in self.filtered("propagate_lot_field_ids"):
            if not production.lot_producing_id:
                raise UserError(
                    self.env._(
                        "Lot field propagation requires a finished product "
                        "lot/serial number."
                    )
                )
            values = production._get_lot_info_propagation_values()
            if values:
                production.lot_producing_id.write(values)

    def _propagate_lot_info_to_byproducts(self):
        for production in self.filtered("propagate_lot_field_ids"):
            values = production._get_lot_info_propagation_values()
            if not values:
                continue
            byproduct_lots = production.move_byproduct_ids.filtered(
                lambda move: move.byproduct_id.propagate_lot_info
            ).move_line_ids.lot_id
            if byproduct_lots:
                byproduct_lots.write(values)

    def _get_lot_info_propagation_values(self):
        self.ensure_one()
        source_lot = self._get_lot_info_propagation_source_lots()
        values = {}
        for field in self.propagate_lot_field_ids:
            value = source_lot[field.name]
            if not value:
                continue
            values[field.name] = value.id if field.ttype == "many2one" else value
        return values
