# Copyright 2025 Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import Command, api, fields, models
from odoo.tools import float_compare, float_round


class MrpProductionSplit(models.TransientModel):
    _inherit = "mrp.production.split"

    max_batch_size = fields.Float(
        compute="_compute_max_batch_size",
        digits="Product Unit",
        readonly=False,
        help="Maximum batch size based on BoM configuration",
    )
    num_splits = fields.Integer(
        "# Splits", compute="_compute_num_splits", readonly=True
    )
    enable_batch_size = fields.Boolean(
        related="production_id.bom_id.enable_batch_size",
    )

    @api.depends("production_id")
    def _compute_max_batch_size(self):
        for wizard in self:
            bom_id = wizard.production_id.bom_id
            wizard.max_batch_size = (
                bom_id.batch_size if bom_id.enable_batch_size else wizard.product_qty
            )

    @api.depends("production_id", "max_batch_size", "product_qty")
    def _compute_num_splits(self):
        """Calculate number of splits based on batch size"""
        for wizard in self:
            wizard.num_splits = 0
            bom_id = wizard.production_id.bom_id
            if (
                bom_id
                and bom_id.enable_batch_size
                and float_compare(
                    wizard.max_batch_size,
                    0,
                    precision_rounding=wizard.product_uom_id.rounding,
                )
                > 0
            ):
                wizard.num_splits = float_round(
                    wizard.product_qty / wizard.max_batch_size,
                    precision_digits=0,
                    rounding_method="UP",
                )
            # Also update counter to trigger planning lines
            wizard.counter = wizard.num_splits

    @api.depends("counter", "num_splits")
    def _compute_details(self):
        """Override to use batch size logic when enabled"""
        for wizard in self:
            bom_id = wizard.production_id.bom_id
            # Use batch size logic if enabled, otherwise use base logic
            if bom_id and bom_id.enable_batch_size and wizard.num_splits > 0:
                commands = [Command.clear()]
                remaining_qty = wizard.product_qty
                for _ in range(wizard.num_splits):
                    qty = min(wizard.max_batch_size, remaining_qty)
                    commands.append(
                        Command.create(
                            {
                                "quantity": qty,
                                "user_id": wizard.production_id.user_id.id,
                                "date": wizard.production_id.date_start,
                            }
                        )
                    )
                    remaining_qty = float_round(
                        remaining_qty - qty,
                        precision_rounding=wizard.product_uom_id.rounding,
                    )
                wizard.production_detailed_vals_ids = commands
            else:
                # Use base Odoo 17.0 logic
                return super()._compute_details()
