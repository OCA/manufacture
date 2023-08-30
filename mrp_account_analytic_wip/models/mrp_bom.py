# Copyright (C) 2023 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    active_ref_bom = fields.Boolean(string="Active Reference BOM")

    def _prepare_raw_tracking_item_values(self, product_uom_qty):
        self.ensure_one()
        product = self.product_tmpl_id or self.product_id
        bom_qty = self.product_uom_id._compute_quantity(
            self.product_qty, product.uom_id
        )
        factor = product_uom_qty / bom_qty
        # Each distinct Product will be one Tracking Item
        # So multiple BOM lines for the same Product need to be aggregated
        lines = self.bom_line_ids
        return [
            {
                "product_id": product.id,
                "planned_qty": sum(
                    x.product_qty for x in lines if x.product_id == product
                )
                * factor,
            }
            for product in lines.product_id
        ]

    def _prepare_ops_tracking_item_values(self, product_uom_qty):
        self.ensure_one()
        # Each distinct Work Center will be one Tracking Item
        # So multiple BOM lines for the same Work Center need to be aggregated
        product = self.product_tmpl_id or self.product_id
        bom_qty = self.product_uom_id._compute_quantity(
            self.product_qty, product.uom_id
        )
        factor = product_uom_qty / bom_qty
        lines = self.operation_ids
        return [
            {
                "product_id": workcenter.analytic_product_id.id,
                "workcenter_id": workcenter.id,
                "planned_qty": sum(
                    x.time_cycle for x in lines if x.workcenter_id == workcenter
                )
                * factor
                / 60,
            }
            for workcenter in lines.workcenter_id
        ]

    def _get_impacted_products(self):
        variant_products = self.product_id
        template_boms = self.filtered(lambda x: not x.product_id)
        template_products = template_boms.product_tmpl_id.product_variant_ids
        return variant_products | template_products

    def _populate_production_tracking_items(self):
        # Identify open MOS impacted by these BOMs
        # And re-populate their Reference BOM Tracking Items
        products = self._get_impacted_products()
        productions = self.env["mrp.production"].search(
            [
                ("product_id", "in", products.ids),
                ("state", "not in", ["done", "cancel"]),
                ("analytic_account_id", "!=", False),
            ],
        )
        # Update Tracking Items, for possible new lines and standard amount changes
        productions.populate_ref_bom_tracking_items()
        # Post WIP based on the changes
        productions.filtered("is_post_wip_automatic").action_post_inventory_wip()

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res.filtered("active_ref_bom")._populate_production_tracking_items()
        return res

    def write(self, vals):
        res = super().write(vals)
        if "active_ref_bom" in vals:
            self._populate_production_tracking_items()
        return res
