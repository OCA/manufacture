# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class RepairComponentOperation(models.Model):
    _name = "repair.component.operation"
    _description = "Repair Component Operation"
    _order = "sequence,id"

    name = fields.Char(help="Component Operation Reference", required=True)

    source_location_id = fields.Many2one(
        "stock.location",
        "Source Location",
        help="The Location where the components are.",
    )

    source_route_id = fields.Many2one(
        comodel_name="stock.location.route",
        string="Source Route",
        help="The Route used to pick the components.",
        domain=[("repair_component_selectable", "=", True)],
    )

    destination_location_id = fields.Many2one(
        "stock.location",
        "Destination Location",
        help="The Location where the components are going to be transferred.",
    )

    destination_route_id = fields.Many2one(
        comodel_name="stock.location.route",
        string="Destination Route",
        help="The Route used to transfer the components to the destination location.",
        domain=[("repair_component_selectable", "=", True)],
    )

    scrap_location_id = fields.Many2one(
        "stock.location",
        "Scrap Location",
    )

    incoming_operation = fields.Selection(
        selection=[
            ("no", "No"),
            ("replace", "Pick Component from Source Route"),
        ],
        default="no",
        required=True,
    )

    outgoing_operation = fields.Selection(
        selection=[
            ("no", "No"),
            ("move", "Move to Destination Location"),
            ("scrap", "Make a Scrap"),
        ],
        default="no",
        required=True,
    )

    picking_type_id = fields.Many2one(
        "stock.picking.type",
        "Operation Type",
        # domain="[('code', '=', 'mrp_operation')]",
    )

    sequence = fields.Integer(
        string="Sequence",
        help="Gives the sequence order when displaying the list of component operations",
    )
    active = fields.Boolean(default=True)
