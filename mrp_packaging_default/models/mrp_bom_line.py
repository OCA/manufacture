# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    product_packaging_id = fields.Many2one(
        comodel_name="product.packaging",
        string="Packaging",
        compute="_compute_product_packaging",
        store=True,
        readonly=False,
        domain="[('product_id', '=', product_id)]",
        check_company=True,
    )
    product_packaging_qty = fields.Float(
        string="Packaging Qty.",
        compute="_compute_product_packaging",
        digits="Product Unit of Measure",
        store=True,
        readonly=False,
    )

    @api.depends("product_id", "product_qty", "product_uom_id")
    def _compute_product_packaging(self):
        """Set the appropriate packaging for the product qty."""
        for one in self:
            one.product_packaging_id = (
                one.product_id.packaging_ids._find_suitable_product_packaging(
                    one.product_qty, one.product_uom_id
                )
            )
            if not one.product_packaging_id:
                one.product_packaging_qty = 0
                continue
            uom_qty_per_package = (
                one.product_packaging_id.product_uom_id._compute_quantity(
                    one.product_packaging_id.qty, one.product_uom_id
                )
            )
            one.product_packaging_qty = (
                one.product_packaging_id._check_qty(one.product_qty, one.product_uom_id)
                / uom_qty_per_package
            )

    @api.onchange("product_packaging_id", "product_packaging_qty")
    def _onchange_product_packaging_set_qty(self):
        """When interactively setting a new packaging, set default qty values."""
        if not self.product_packaging_id:
            return
        self.product_qty = (
            self.product_packaging_qty
            * self.product_uom_id._compute_quantity(
                self.product_packaging_id.qty,
                self.product_packaging_id.product_uom_id,
            )
        )

    @api.onchange("product_id")
    def _onchange_product_set_qty_from_packaging(self):
        """When interactively setting a new product, set default packaging values."""
        default_packaging = self.product_id.packaging_ids[:1]
        if default_packaging:
            self.product_uom_id = default_packaging.product_uom_id
            self.product_qty = default_packaging.qty
