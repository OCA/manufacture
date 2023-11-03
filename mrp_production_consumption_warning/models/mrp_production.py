# Copyright 2023 Komit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    consumption_warning_msg = fields.Text(compute="_compute_consumption_warning_msg")

    @api.depends(
        "bom_id",
        "bom_id.bom_line_ids",
        "bom_id.bom_line_ids.product_id",
        "bom_id.bom_line_ids.product_qty",
        "move_raw_ids",
        "move_raw_ids.product_id",
    )
    def _compute_consumption_warning_msg(self):
        for rec in self:
            rec.consumption_warning_msg = ""
            bom_line_ids = rec.bom_id.bom_line_ids
            # The components have in BoM but not in MO
            unused_products = (
                bom_line_ids.filtered(
                    lambda l: l.child_bom_id.type != "phantom"
                ).product_id
                - rec.move_raw_ids.product_id
            )
            if unused_products:
                rec.consumption_warning_msg += _(
                    "- The MO does not use the product(s) %(names)s\n",
                    names=", ".join(unused_products.mapped(lambda x: x.display_name)),
                )
            # The components have wrong quantity
            for move_raw in rec.move_raw_ids:
                kit_component_qty = (
                    bom_line_ids.filtered(
                        lambda l: l.product_tmpl_id
                        == move_raw.bom_line_id.bom_id.product_tmpl_id
                    ).product_qty
                    or 1
                )
                if (
                    move_raw.bom_line_id
                    and move_raw.product_uom_qty
                    != move_raw.bom_line_id.product_qty * kit_component_qty
                ):
                    rec.consumption_warning_msg += _(
                        "- The MO line quantity for Product %(product)s is %(w_qty)s "
                        "instead of %(r_qty)s on the BoM line\n",
                        product=", ".join(
                            move_raw.product_id.mapped(lambda x: x.display_name)
                        ),
                        w_qty=move_raw.product_uom_qty,
                        r_qty=move_raw.bom_line_id.product_qty * kit_component_qty,
                    )
            # The components have in MO but not in BoM
            unpresent_products = (
                rec.move_raw_ids.filtered(
                    lambda m: m.bom_line_id.bom_id.type != "phantom"
                ).product_id
                - bom_line_ids.product_id
            )
            if unpresent_products:
                rec.consumption_warning_msg += _(
                    "- The components %(names)s is/are not present on the BoM\n",
                    names=", ".join(
                        unpresent_products.mapped(lambda x: x.display_name)
                    ),
                )

            if rec.consumption_warning_msg != "":
                rec.consumption_warning_msg = (
                    "There are discrepancies between your Manufacturing Order and "
                    "the BoM associated with the Finished products:\n"
                    + rec.consumption_warning_msg
                )
