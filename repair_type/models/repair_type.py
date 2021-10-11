# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import fields, models


class RepairType(models.Model):
    _name = "repair.type"
    _description = "Repair Type"

    name = fields.Char("Repair Type Name", copy=False, required=True)
    source_location_id = fields.Many2one(
        "stock.location",
        "Source Location",
        help="This is the location where the product to repair is located.",
    )
    destination_location_id = fields.Many2one(
        "stock.location",
        "Destination Location",
        help="This is the location where the product repaired will be located.",
    )
    source_location_add_part_id = fields.Many2one(
        "stock.location",
        "Source Location Add Component",
        help="This is the location where the part of the product to add is located.",
    )
    destination_location_add_part_id = fields.Many2one(
        "stock.location",
        "Destination Location Add Component",
        help="This is the location where the part of the product to add is located.",
    )
    source_location_remove_part_id = fields.Many2one(
        "stock.location",
        "Source Location Remove Component",
        help="This is the location where the part of the product to remove is located.",
    )
    destination_location_remove_part_id = fields.Many2one(
        "stock.location",
        "Destination Location Remove Component",
        help="This is the location where the part of the product to remove is located.",
    )
