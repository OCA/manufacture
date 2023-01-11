# Copyright 2019-20 ForgeFlow S.L. (http://www.forgeflow.com)
# - Lois Rilo Antelo <lois.rilo@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductMRPArea(models.Model):
    _inherit = "product.mrp.area"

    group_estimate_days = fields.Integer(
        string="Group Days of Estimates",
        default=1,
        help="The days to group your estimates as demand for the MRP."
        "It can be different from the length of the date ranges you "
        "use in the estimates but it should not be greater, in that case"
        "only grouping until the total length of the date range will be done.",
    )

    _sql_constraints = [
        (
            "group_estimate_days_check",
            "CHECK( group_estimate_days >= 0 )",
            "Group Days of Estimates must be greater than or equal to zero.",
        ),
    ]
