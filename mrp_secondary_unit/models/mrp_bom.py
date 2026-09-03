# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

MRP_SECONDARY_UNIT_QTY_FIELD = {
    "store": True,
    "readonly": False,
    "compute": "_compute_product_qty",
    "precompute": True,
    "default": None,
}


class MrpBom(models.Model):
    _name = "mrp.bom"
    _inherit = ["mrp.bom", "mrp.bom.secondary.unit.mixin"]

    product_qty = fields.Float(**MRP_SECONDARY_UNIT_QTY_FIELD)

    def _get_product_uom(self):
        self.ensure_one()
        return (self.product_id or self.product_tmpl_id)[self._product_uom_field]

    def _get_product_secondary_uom(self):
        """A bill of materials is defined on the template, and only optionally
        narrowed down to one of its variants."""
        self.ensure_one()
        return (
            self.product_id.stock_secondary_uom_id
            or self.product_tmpl_id.stock_secondary_uom_id
        )

    @api.onchange("product_tmpl_id")
    def onchange_product_tmpl_id_for_secondary(self):
        self.onchange_product_id_for_secondary()


class MrpBomLine(models.Model):
    _name = "mrp.bom.line"
    _inherit = ["mrp.bom.line", "mrp.bom.secondary.unit.mixin"]

    product_qty = fields.Float(**MRP_SECONDARY_UNIT_QTY_FIELD)


class MrpBomByproduct(models.Model):
    _name = "mrp.bom.byproduct"
    _inherit = ["mrp.bom.byproduct", "mrp.bom.secondary.unit.mixin"]

    product_qty = fields.Float(**MRP_SECONDARY_UNIT_QTY_FIELD)
