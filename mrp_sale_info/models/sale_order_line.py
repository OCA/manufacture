# Copyright 2024 Camptocamp SA
# Copyright 2024 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import operator
from functools import reduce

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    created_production_ids = fields.Many2many(
        "mrp.production",
        compute="_compute_created_production_ids",
        store=True,
    )

    @api.depends(lambda sol: sol._created_prod_move_deps())
    def _compute_created_production_ids(self):
        move_to_production_ids = dict()
        for move in self.move_ids:
            productions = move._get_orig_created_production_ids()
            productions |= productions.procurement_group_id.mrp_production_ids
            move_to_production_ids[move] = productions

        for line in self:
            delivery_moves = line.move_ids
            productions = reduce(
                operator.or_,
                [
                    move_to_production_ids[delivery_move]
                    for delivery_move in delivery_moves
                ],
                self.env["mrp.production"].browse(),
            )
            line.created_production_ids = productions

    def _created_prod_move_deps(self):
        fnames = [
            "move_ids",
            "move_ids.created_production_id",
            "move_ids.created_production_id.procurement_group_id.mrp_production_ids",
        ]
        # Allow customizing how many levels of recursive moves must be considered to
        #  compute the created_production_ids field on sale.order.line.
        # This value must be at least equal to the number of:
        #  delivery steps + post manufacturing operations of the warehouse - 1.
        # FIXME: Check if there's a way to recompute the dependency without having to
        #  restart Odoo.
        try:
            levels = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("mrp_sale_info.compute.created_prod_ids_move_dep_levels", 3)
            )
        except ValueError:
            levels = 3
        for num in range(1, levels + 1):
            fnames.append("move_ids.%screated_production_id" % ("move_orig_ids." * num))
            fnames.append(
                "move_ids.%screated_production_id.procurement_group_id.mrp_production_ids"
                % ("move_orig_ids." * num)
            )
        return fnames
