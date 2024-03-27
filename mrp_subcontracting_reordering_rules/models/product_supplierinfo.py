from odoo import api, fields, models


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    route_id = fields.Many2one(
        comodel_name="stock.location.route", string="Preferred Route"
    )
    trigger = fields.Selection(
        [("auto", "Auto"), ("manual", "Manual")],
        string="Trigger",
        default="manual",
        required=True,
    )
    order_points_ids = fields.One2many(
        comodel_name="stock.warehouse.orderpoint", inverse_name="supplier_id"
    )

    def _compute_is_subcontractor(self):
        super(ProductSupplierInfo, self)._compute_is_subcontractor()
        self._compute_update_orderpoints()

    def _prepare_selected_product_variant(self):
        """Preparing order points if selected product variant"""
        self.ensure_one()
        order_points = self.with_context(active_test=False).order_points_ids
        record = order_points.filtered(lambda p: p.product_id == self.product_id)
        (order_points.filtered(lambda o: o.active) - record).write({"active": False})
        if record:
            record.write(
                {
                    "location_id": self.name.property_stock_subcontractor.id,
                    "route_id": self.route_id.id,
                    "trigger": self.trigger,
                    "active": True,
                }
            )
        elif self.product_id in self.product_tmpl_id.product_variant_ids:
            self._create_sw_order_points(self.product_id)

    def _prepare_selected_no_product_variants(self):
        """Preparing order points if product variant is no selected"""
        self.ensure_one()
        order_points = self.with_context(active_test=False).order_points_ids
        products = order_points.filtered(lambda o: not o.active).mapped("product_id")
        variant_ids = self.product_tmpl_id.product_variant_ids.filtered(
            lambda p: p not in products.ids
        )
        all_variants = order_points.filtered(lambda o: o.product_id in variant_ids)
        if all_variants:
            all_variants.write({"active": True})
        create_variants = variant_ids.filtered(
            lambda v: v not in all_variants.mapped("product_id")
        )
        if create_variants:
            self._create_sw_order_points(create_variants)
        else:
            order_points.filtered(lambda o: o.active).write(
                {
                    "location_id": self.name.property_stock_subcontractor.id,
                    "route_id": self.route_id.id,
                    "trigger": self.trigger,
                    "active": True,
                }
            )

    @api.depends(
        "product_id",
        "product_tmpl_id",
        "product_tmpl_id.attribute_line_ids",
        "route_id",
        "trigger",
    )
    def _compute_update_orderpoints(self):
        """Create or update reordering rules"""
        active_subcontractor = self.filtered(lambda r: r.is_subcontractor)
        for supplier in active_subcontractor:
            # selected product variant
            if supplier.product_id:
                supplier._prepare_selected_product_variant()
            # no product variant selected, so we create for all variants
            else:
                supplier._prepare_selected_no_product_variants()
        inactive_subcontractor = self - active_subcontractor
        for supplier in inactive_subcontractor:
            supplier.order_points_ids.write({"active": False})

    def _create_sw_order_points(self, products):
        """Create not existing order points"""
        self.ensure_one()
        exclude_products = self.order_points_ids.mapped("product_id").filtered(
            lambda p: p not in products
        )
        products = products - exclude_products
        products_vals = list(
            map(
                lambda p: {
                    "product_id": p.id,
                    "product_min_qty": 0,
                    "product_max_qty": 0,
                    "qty_multiple": 1,
                    "location_id": self.name.property_stock_subcontractor.id,
                    "route_id": self.route_id.id,
                    "trigger": self.trigger,
                    "supplier_id": self.id,
                },
                products,
            )
        )
        return self.write(
            {
                "order_points_ids": [
                    (0, 0, product_vals) for product_vals in products_vals
                ]
            }
        )

    def unlink(self):
        self.with_context(active_test=False).mapped("order_points_ids").unlink()
        return super(ProductSupplierInfo, self).unlink()
