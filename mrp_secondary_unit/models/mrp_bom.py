# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

MRP_SECONDARY_UNIT_QTY_FIELD = {
    "store": True,
    "readonly": False,
    "compute": "_compute_product_qty",
    "precompute": True,
    "default": None,
}


class MrpBom(models.Model):
    _name = "mrp.bom"
    _inherit = ["mrp.bom", "mrp.secondary.unit.mixin"]

    product_qty = fields.Float(**MRP_SECONDARY_UNIT_QTY_FIELD)

    def _get_product_uom(self):
        self.ensure_one()
        return (self.product_id or self.product_tmpl_id)[self._product_uom_field]


class MrpBomLine(models.Model):
    _name = "mrp.bom.line"
    _inherit = ["mrp.bom.line", "mrp.secondary.unit.mixin"]

    product_qty = fields.Float(**MRP_SECONDARY_UNIT_QTY_FIELD)


class MrpBomByproduct(models.Model):
    _name = "mrp.bom.byproduct"
    _inherit = ["mrp.bom.byproduct", "mrp.secondary.unit.mixin"]

    product_qty = fields.Float(**MRP_SECONDARY_UNIT_QTY_FIELD)
