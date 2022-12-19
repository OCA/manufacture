# Copyright 2022 ForgeFlow S.L. (http://www.forgeflow.com)
# - Lois Rilo Antelo <lois.rilo@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MRPArea(models.Model):
    _inherit = "mrp.area"

    estimate_demand_and_other_sources_strat = fields.Selection(
        string="Demand Estimates and Other Demand Sources Strategy",
        selection=[
            ("all", "Always consider all sources"),
            (
                "ignore_others_if_estimates",
                "Ignore other sources for products with estimates",
            ),
            (
                "ignore_overlapping",
                "Ignore other sources during periods with estimates",
            ),
        ],
        default="all",
        help="Define the strategy to follow in MRP multi level when there is a"
        "coexistence of demand from demand estimates and other sources.\n"
        "* Always consider all sources: nothing is excluded or ignored.\n"
        "* Ignore other sources for products with estimates: When there "
        "are estimates entered for product and they are in a present or "
        "future period, all other sources of demand are ignored for those "
        "products.\n"
        "* Ignore other sources during periods with estimates: When "
        "you create demand estimates for a period and product, "
        "other sources of demand will be ignored during that period "
        "for those products.",
    )
