# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class MrpBomSecondaryUnitMixin(models.AbstractModel):
    _name = "mrp.bom.secondary.unit.mixin"
    _inherit = "product.secondary.unit.mixin"
    _description = "MRP BoM Secondary Unit Mixin"
    _secondary_unit_fields = {
        "qty_field": "product_qty",
        "uom_field": "product_uom_id",
    }

    @api.model
    def _get_default_value_for_qty_field(self):
        return 1.0

    def _get_product_secondary_uom(self):
        """Default to the inventory secondary unit, as what is manufactured
        goes straight to stock."""
        self.ensure_one()
        return (
            self.product_id.stock_secondary_uom_id
            or self.product_id.product_tmpl_id.stock_secondary_uom_id
        )

    @api.onchange("product_id")
    def onchange_product_id_for_secondary(self):
        product_secondary_uom = self._get_product_secondary_uom()
        if self.secondary_uom_id != product_secondary_uom:
            self.secondary_uom_id = product_secondary_uom
            # A saved record keeps its quantity, as when switching the unit.
            if self._origin.id:
                self._onchange_helper_product_uom_for_secondary()
            elif product_secondary_uom:
                self.secondary_uom_qty = 1.0

    @api.model
    def _get_secondary_uom_qty_depends(self):
        # The factor refers to the unit of the product, so the secondary
        # quantity has to be converted again when the unit of the line changes.
        return super()._get_secondary_uom_qty_depends() + ["product_uom_id"]

    @api.onchange("secondary_uom_id")
    def _onchange_secondary_uom_id_for_qty(self):
        """Switching the secondary unit keeps the quantity, as on a
        manufacturing order, instead of rescaling it with the new factor."""
        self._derive_secondary_uom_qty()
        return super()._onchange_secondary_uom_id_for_qty()

    def write(self, vals):
        # A unit written alone keeps the quantity, as when picked in the form.
        res = super().write(vals)
        qty_fields = {"secondary_uom_qty", self._secondary_unit_fields["qty_field"]}
        if "secondary_uom_id" in vals and not qty_fields & vals.keys():
            self._derive_secondary_uom_qty()
        return res

    @api.depends("secondary_uom_qty")
    def _compute_product_qty(self):
        self._compute_helper_target_field_qty()

    def _compute_helper_target_field_qty(self):
        return super(
            MrpBomSecondaryUnitMixin, self._keep_qty_matching_secondary()
        )._compute_helper_target_field_qty()
