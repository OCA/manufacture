# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    mrp_workcenter_cost = fields.Selection(
        selection=[("theoretical", "Theoretical"), ("effective", "Effective")],
        string="Workcenter Cost Duration",
        help="Controls how to compute the workcenter cost for manufactured products.\n"
        "* Theoretical: The cost is computed based on the theoretical duration of the "
        "workcenter.\n"
        "* Effective: The cost is computed based on the real duration of the workcenter.",
        default="effective",
        required=True,
    )
