# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    currency_id = fields.Many2one(related="product_tmpl_id.currency_id")

    # Fields related to standard price
    product_standard_price = fields.Float(compute="_compute_product_standard_price")
    standard_price = fields.Float(
        string="BoM Unit Cost",
        tracking=True,
        digits="Product Price",
        compute="_compute_standard_price",
        help="Calculated with raw components cost divided by the BoM quantity.",
    )
    diff_product_bom_standard_price = fields.Boolean(
        default=False,
        compute="_compute_diff_product_bom_standard_price",
    )

    # Fields related to sale price
    product_sale_price = fields.Float(
        string="Product Sale Price", related="product_id.lst_price"
    )
    product_margin_rate = fields.Float(related="product_id.standard_margin_rate")
    product_margin_rate_percentage = fields.Float(
        string="Product Margin", compute="_compute_product_margin_rate_percentage"
    )

    # Compute functions
    @api.depends("product_id", "product_id.standard_price")
    def _compute_product_standard_price(self):
        for bom in self:
            bom.product_standard_price = bom.product_id.standard_price

    @api.depends("product_id", "bom_line_ids", "product_qty")
    def _compute_standard_price(self):
        for bom in self:
            qty_to_divide = bom.product_qty if bom.product_qty != 0 else 1
            bom.standard_price = (
                sum(x.standard_price_subtotal for x in bom.bom_line_ids) / qty_to_divide
            )

    @api.depends("product_id.standard_price", "standard_price")
    def _compute_diff_product_bom_standard_price(self):
        price_dp = self.env["decimal.precision"].precision_get("Product Price")
        for bom in self:
            if bom.product_id:
                diff = bom.product_id.standard_price - bom.standard_price
                bom.diff_product_bom_standard_price = float_round(diff, price_dp)
            else:
                bom.diff_product_bom_standard_price = False

    @api.depends("product_margin_rate")
    def _compute_product_margin_rate_percentage(self):
        for bom in self:
            bom.product_margin_rate_percentage = bom.product_margin_rate / 100

    # Functions to change product fields
    def set_product_standard_price(self):
        for bom in self.filtered(lambda x: x.product_id):
            bom.product_id.standard_price = bom.standard_price
