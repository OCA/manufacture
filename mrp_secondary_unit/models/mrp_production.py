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
        # See ``product_qty`` in ``mrp.secondary.unit.mixin``: the default the
        # mixin sets would be taken as a provided value at creation and would
        # keep the compute below from running.
        default=None,
    )

    @api.depends("bom_id")
    def _compute_secondary_uom_id(self):
        """Take the secondary unit the finished product is produced in from the
        bill of materials, so that the order is expressed in the same unit as
        the recipe it comes from.
        """
        for production in self:
            production.secondary_uom_id = production.bom_id.secondary_uom_id

    @api.model
    def _get_secondary_uom_qty_depends(self):
        # The factor refers to the unit of the product, so a change of the unit
        # of the order changes the secondary quantity as well. Picking a
        # secondary unit therefore derives the secondary quantity from the
        # quantity to produce, and never the other way around: the quantity to
        # produce comes from the bill of materials or from the procurement that
        # asked for the order, and only a secondary quantity the user enters
        # himself may drive it.
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
        """Set the quantity to produce out of the secondary one.

        Done here rather than by adding the secondary fields to the
        dependencies of ``product_qty``: that field is already computed by
        ``mrp``, and its method resets the quantity to the one of the bill of
        materials whenever it runs on a record whose bill of materials differs
        from the one of its origin, which is always the case for an order being
        created. Making it depend on the secondary fields would run that reset
        again every time the secondary quantity is edited and discard the
        quantity the user asked for.
        """
        self.filtered(lambda p: p.state == "draft")._compute_helper_target_field_qty()

    def _propagate_secondary_uom_to_finished_move(self):
        """Set the secondary unit on the move of the finished product.

        ``_get_move_finished_values`` already puts it on the values of the
        move, but that move appears in no view, so a client saving the order
        sends the moves it holds back without it and the value is lost. Only
        moves that come out without a secondary unit are touched, so a value
        set anywhere else is kept.
        """
        for production in self.filtered("secondary_uom_id"):
            moves = production.move_finished_ids.filtered(
                lambda m, p=production: not m.byproduct_id
                and m.product_id == p.product_id
                and not m.secondary_uom_id
            )
            secondary_uom = production.secondary_uom_id
            for move in moves:
                # The three values go in a single write on purpose. On a move
                # the secondary quantity is what drives the primary one, so
                # writing the unit alone would recompute the quantity to
                # consume out of a secondary quantity that is still zero, and
                # writing the derived secondary quantity alone would let its
                # rounding shift the quantity the order was exploded with.
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
        """Values setting the secondary unit of a generated move.

        Only the unit comes from the bill of materials: the quantity is the one
        exploded from it in the primary unit, and the secondary quantity is
        derived back from that. The derived quantity has to be part of the same
        values, and not left to the compute of the mixin, because on a move it
        is the secondary quantity that drives the primary one. Values holding
        the unit alone are applied to an existing move by
        ``_compute_move_raw_ids`` when the quantity to produce changes, and the
        quantity that was just exploded would then be overwritten by the
        secondary quantity the move still carries from the previous quantity.

        An ``independent`` secondary quantity cannot be derived from the
        primary one, so it is left alone.
        """
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
