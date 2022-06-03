import logging

from odoo import api, fields, models

logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_bom_vendor_price(self):
        templates = self.filtered(
            lambda t: t.product_variant_count == 1 and t.bom_count > 0
        )
        if templates:
            return templates.mapped("product_variant_id").action_bom_vendor_price()


class ProductProduct(models.Model):
    _inherit = "product.product"

    cost_vendor_price = fields.Float(
        groups="mrp.group_mrp_user",
        readonly=True,
        help="Cost based on bom and vendor price",
    )
    vendor_price_id = fields.Many2one(
        comodel_name="product.supplierinfo",
        string="Vendor price line",
        groups="mrp.group_mrp_user",
        help="Main vendor price used to compute",
    )

    def action_bom_vendor_price(self):
        for product in self:
            bom = self.env["mrp.bom"]._bom_find(product=product)
            if bom:
                bom.product_tmpl_id.product_variant_ids[
                    0
                ].cost_vendor_price = bom._compute_cost_with_vendor_price()

    def set_vendor_price(self):
        product_count = 0
        for product in self:
            # You may change vendor_info selection
            # overiding _select_seller() according to the context
            vendor_info = product.with_context(
                self._get_ctx_vendor_price_case()
            )._select_seller(uom_id=product.uom_id)
            vals = {}
            if vendor_info:
                if vendor_info.price != product.cost_vendor_price:
                    vals["cost_vendor_price"] = vendor_info.price
                    product_count += 1
                if vendor_info != product.vendor_price_id:
                    vals["vendor_price_id"] = vendor_info.id
            elif product.vendor_price_id:
                vals["vendor_price_id"] = False
                vals["cost_vendor_price"] = 0
            if vals:
                product.write(vals)
        return product_count

    @api.model
    def _get_ctx_vendor_price_case(self):
        return {"force_company": 1, "from_vendor_price": True}
