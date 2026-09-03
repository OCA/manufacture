# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _name = "mrp.production"
    _inherit = ["mrp.production", "product.secondary.unit.mixin"]
    _secondary_unit_fields = {
        "qty_field": "product_qty",
        "uom_field": "product_uom_id",
    }

    secondary_uom_id = fields.Many2one(
        compute="_compute_secondary_uom_id",
        store=True,
        readonly=False,
        precompute=True,
        default=None,
    )

    @api.depends("bom_id")
    def _compute_secondary_uom_id(self):
        for production in self:
            production.secondary_uom_id = production.bom_id.secondary_uom_id

    @api.model
    def _get_secondary_uom_qty_depends(self):
        return super()._get_secondary_uom_qty_depends() + [
            "product_uom_id",
            "secondary_uom_id",
        ]

    @api.onchange("secondary_uom_qty")
    def onchange_secondary_uom_qty(self):
        self._set_product_qty_from_secondary()

    @api.model_create_multi
    def create(self, vals_list):
        productions = super().create(vals_list)
        driven = self.browse()
        for production, vals in zip(productions, vals_list, strict=True):
            if self._is_driven_by_secondary_uom(vals):
                driven |= production
        driven._set_product_qty_from_secondary()
        productions._propagate_secondary_uom_to_finished_move()
        return productions

    def write(self, vals):
        res = super().write(vals)
        if self._is_driven_by_secondary_uom(vals):
            self._set_product_qty_from_secondary()
        if "secondary_uom_id" in vals or "move_finished_ids" in vals:
            self._propagate_secondary_uom_to_finished_move()
        return res

    @api.model
    def _is_driven_by_secondary_uom(self, vals):
        return "product_qty" not in vals and "secondary_uom_qty" in vals

    def _set_product_qty_from_secondary(self):
        self.filtered(lambda p: p.state == "draft")._compute_helper_target_field_qty()

    def _propagate_secondary_uom_to_finished_move(self):
        for production in self.filtered("secondary_uom_id"):
            moves = production.move_finished_ids.filtered(
                lambda m, p=production: not m.byproduct_id
                and m.product_id == p.product_id
                and not m.secondary_uom_id
            )
            secondary_uom = production.secondary_uom_id
            if secondary_uom.dependency_type != "dependent":
                continue
            for move in moves:
                move.write(
                    {
                        "secondary_uom_id": secondary_uom.id,
                        "secondary_uom_qty": secondary_uom._get_secondary_qty(
                            move.product_uom_qty, move.product_uom
                        ),
                        "product_uom_qty": move.product_uom_qty,
                    }
                )

    @api.model
    def _get_secondary_uom_move_vals(self, secondary_uom, product_uom_qty, product_uom):
        if not secondary_uom:
            return {}
        vals = {"secondary_uom_id": secondary_uom.id}
        if secondary_uom.dependency_type == "dependent":
            vals["secondary_uom_qty"] = secondary_uom._get_secondary_qty(
                product_uom_qty, product_uom
            )
        return vals

    def _get_move_raw_values(
        self, product, product_uom_qty, product_uom, operation_id=False, bom_line=False
    ):
        """Carry the secondary unit of the component over to the generated move."""
        vals = super()._get_move_raw_values(
            product, product_uom_qty, product_uom, operation_id, bom_line
        )
        if bom_line:
            vals.update(
                self._get_secondary_uom_move_vals(
                    bom_line.secondary_uom_id, product_uom_qty, product_uom
                )
            )
        return vals

    def _get_move_finished_values(
        self,
        product_id,
        product_uom_qty,
        product_uom,
        operation_id=False,
        byproduct_id=False,
        cost_share=0,
    ):
        vals = super()._get_move_finished_values(
            product_id,
            product_uom_qty,
            product_uom,
            operation_id,
            byproduct_id,
            cost_share,
        )
        byproduct = self.env["mrp.bom.byproduct"].browse(byproduct_id)
        secondary_uom = (
            byproduct.secondary_uom_id if byproduct else self.secondary_uom_id
        )
        vals.update(
            self._get_secondary_uom_move_vals(
                secondary_uom, product_uom_qty, self.env["uom.uom"].browse(product_uom)
            )
        )
        return vals
