# Copyright 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpRequestWorkcenter(models.Model):
    _name = "mrp.request.workcenter"
    _description = "Workcenters attached to Production Request"

    request_id = fields.Many2one(
        comodel_name="mrp.production.request", string="Production Request"
    )
    workcenter_id = fields.Many2one(
        comodel_name="mrp.workcenter", string="Workcenter", required=True
    )
    workcenter_cycle_no = fields.Float(
        string="Cycles",
        default="1",
        help="A cycle is complete ended process for the machine.\n"
        "Multiple cycles are several machines of the same kind in parallel "
        "or the same machine used several times.",
    )
    product_qty = fields.Float(string="Products by cycle")

    _sql_constraints = [
        (
            "request_workcenter_unique",
            "UNIQUE(workcenter_id,request_id)",
            "Workcenter field must be unique by manufacturing request",
        )
    ]
