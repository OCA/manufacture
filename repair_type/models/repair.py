# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import api, fields, models


class Repair(models.Model):
    _inherit = "repair.order"

    repair_type_id = fields.Many2one(comodel_name="repair.type")
    location_id = fields.Many2one(
        compute="_compute_location_id", store=True, readonly=False
    )

    @api.depends("repair_type_id")
    def _compute_location_id(self):
        for rec in self:
            if rec.repair_type_id.source_location_id:
                rec.location_id = rec.repair_type_id.source_location_id


class RepairLine(models.Model):
    _inherit = "repair.line"

    location_id = fields.Many2one(
        compute="_compute_location_id", store=True, readonly=False
    )
    location_dest_id = fields.Many2one(
        compute="_compute_location_id", store=True, readonly=False
    )

    @api.depends("type", "repair_id.repair_type_id")
    def _compute_location_id(self):
        for rec in self:
            if (
                rec.type == "add"
                and rec.repair_id.repair_type_id.source_location_add_part_id
            ):
                rec.location_id = (
                    rec.repair_id.repair_type_id.source_location_add_part_id
                )
            if (
                rec.type == "add"
                and rec.repair_id.repair_type_id.destination_location_add_part_id
            ):
                rec.location_dest_id = (
                    rec.repair_id.repair_type_id.destination_location_add_part_id
                )
            if (
                rec.type == "remove"
                and rec.repair_id.repair_type_id.source_location_remove_part_id
            ):
                rec.location_id = (
                    rec.repair_id.repair_type_id.source_location_remove_part_id
                )
            if (
                rec.type == "remove"
                and rec.repair_id.repair_type_id.destination_location_remove_part_id
            ):
                rec.location_dest_id = (
                    rec.repair_id.repair_type_id.destination_location_remove_part_id
                )

    @api.onchange("type")
    def onchange_operation_type(self):
        # this onchange was overriding the changes from the compute
        # method `_compute_location_id`, we ensure that the locations
        # in the types have more priority by explicit calling the compute.
        res = super().onchange_operation_type()
        self._compute_location_id()
        return res
