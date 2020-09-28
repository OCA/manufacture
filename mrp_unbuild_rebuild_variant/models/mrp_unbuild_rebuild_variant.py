# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, exceptions, fields, models


class MrpUnbuildRebuildVariant(models.Model):

    _name = "mrp.unbuild.rebuild.variant"
    _description = "Wrapper aroud the unbuild - rebuild process."

    def _get_default_location_id(self):
        # Copied from mrp/models/mrp_unbuild.py
        stock_location = self.env.ref('stock.stock_location_stock', raise_if_not_found=False)
        try:
            stock_location.check_access_rule('read')
            return stock_location.id
        except (AttributeError, exceptions.AccessError):
            return self.env['stock.warehouse'].search(
                [
                    ('company_id', '=', self.env.user.company_id.id)
                ], limit=1
            ).lot_stock_id.id

    name = fields.Char(
        default=lambda self: self.env["ir.sequence"].next_by_code(self._name),
        readonly=True,
    )
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done")],
        required=True,
        default="draft",
        readonly=True,
    )

    # Unbuild fields
    unbuild_product_id = fields.Many2one("product.product", required=True)
    unbuild_bom_id = fields.Many2one(
        "mrp.bom", compute="_compute_unbuild_product_id", required=True,
    )
    # if unbuild product is tracked:
    unbuild_lot_id = fields.Many2one(
        "stock.production.lot",
        domain="[('product_id', '=', unbuild_product_id)]",
    )
    # if unbuild product's bom includes tracked components:
    unbuild_original_mo_id = fields.Many2one(
        "mrp.production",
        domain=(
            "[('product_id', '=', unbuild_product_id),"
            "('state', 'in', ['done', 'cancel'])]"
        ),
    )

    # Common fields
    quantity = fields.Float(default=1.0)
    stock_location_id = fields.Many2one(
        "stock.location", required=True, default=_get_default_location_id
    )
    product_template_id = fields.Many2one(
        "product.template", related="unbuild_product_id.product_tmpl_id"
    )
    product_tracking = fields.Selection(
        string="Product Tracking", related="product_template_id.tracking"
    )

    # Rebuild fields
    rebuild_product_id = fields.Many2one(
        "product.product", domain=("[('product_tmpl_id', '=', product_template_id)]")
    )
    rebuild_bom_id = fields.Many2one("mrp.bom", compute="_compute_rebuild_product_id")
    rebuild_lot_id = fields.Many2one("stock.production.lot")

    unbuild_order_id = fields.Many2one("mrp.unbuild", readonly=True)
    rebuild_order_id = fields.Many2one("mrp.production", readonly=True)

    @api.constrains("unbuild_lot_id")
    def _check_unbuild_lot_id(self):
        if self.product_tracking != "none" and not self.unbuild_lot_id.id:
            raise ValueError(
                _("A lot number should be provided if unbuild product is tracked.")
            )

    @api.constrains("quantity")
    def _check_quantity(self):
        if self.product_tracking != "none" and self.quantity != 1.0:
            raise ValueError(
                _("Quantity should be set to 1.0 if unbuild product is tracked.")
            )


    @api.onchange("rebuild_product_id")
    def _compute_rebuild_product_id(self):
        for record in self:
            if record.rebuild_product_id:
                record.rebuild_bom_id = record.env["mrp.bom"]._bom_find(
                    product=record.rebuild_product_id
                )

    @api.onchange("unbuild_product_id")
    def _compute_unbuild_product_id(self):
        for record in self:
            if record.unbuild_product_id:
                record.unbuild_bom_id = record.env["mrp.bom"]._bom_find(
                    product=record.unbuild_product_id
                )
                record.valid_rebuild_product_ids = [(6, 0, (
                    record.unbuild_product_id.product_tmpl_id.product_variant_ids.ids
                ))]

    def _filter_bom_lines_for_variant(self, lines, variant):
        """
        Filter lines with no attributes or
        where product and line attributes intersection is not null.
        """
        attributes = variant.attribute_value_ids
        lines = lines.filtered(
            lambda l: not l.attribute_value_ids or attributes & l.attribute_value_ids
        )
        return lines

    def _check_dismatled_contains_components(self):
        """
        For the moment, ensure that every component required to build the
        `rebuild` product is a component of the `unbuild` product as well.
        TODO: Find a way to allow user to pick any serial number
        for components picked from the stock.
        """
        # Check 1 : Ensure both variants refers to the same product template
        rebuild_tmpl = self.rebuild_product_id.product_tmpl_id
        unbuild_tmpl = self.unbuild_product_id.product_tmpl_id
        if not (rebuild_tmpl == unbuild_tmpl):
            raise exceptions.ValidationError(
                _("Both unbuild and rebuild products should have the same template.")
            )
        # Check 2 : rebuild product is a subset of unbuild product
        required_bom_components = self._filter_bom_lines_for_variant(
            self.rebuild_bom_id.bom_line_ids, self.rebuild_product_id
        )
        available_bom_components = self._filter_bom_lines_for_variant(
            self.unbuild_bom_id.bom_line_ids, self.unbuild_product_id
        )
        rebuild_product_qties_matrix = [
            (c.product_id, c.product_qty) for c in required_bom_components
        ]
        for product_id, qty in rebuild_product_qties_matrix:
            available_bom_line = available_bom_components.filtered(
                lambda l: l.product_id == product_id
            )
            if not available_bom_line:
                raise exceptions.ValidationError(
                    _("There's no {} in unbuild product.").format(product_id.name)
                )
            total_available = sum(
                [line.product_qty for line in available_bom_line]
            )
            if qty > total_available:
                raise exceptions.ValidationError(
                    _(
                        "There's not enough {} in unbuild product.\n"
                        "{} expected; {} available after dismantling."
                    ).format(product_id.name, qty, total_available)
                )

    def _check_availability(self):
        """
        Checks that all products to create the `rebuild product` are available
        either in the `unbuild product` (by dismantling it) or in the stock.
        """
        applicable_bom_lines = self._filter_bom_lines_for_variant(
            self.rebuild_bom_id.bom_line_ids, self.rebuild_product_id
        )

        product_qty_matrix = [
            (l.product_id, l.product_qty) for l in applicable_bom_lines
        ]

        errors = {}
        unbuild_bom_lines = self._filter_bom_lines_for_variant(
            self.unbuild_bom_id.bom_line_ids, self.unbuild_product_id
        )
        for product, qty in product_qty_matrix:

            # Check substract qty of dismantable components
            unbuild_bom_line = unbuild_bom_lines.filtered(
                lambda l: l.product_id == product
            )
            if unbuild_bom_line:
                qty -= unbuild_bom_line.product_qty

            # Then, substract qty in stock
            in_stock_quants = self.env["stock.quant"].search(
                [
                    ("location_id", "=", self.stock_location_id.id),
                    ("product_id", "=", product.id),
                ]
            )
            qty -= sum([(q.quantity - q.reserved_quantity) for q in in_stock_quants])

            # If qty > 0, then we're `qty` products short to build the product
            if qty > 0:
                errors[product.name] = qty
        if errors:
            error_string = "\n".join(
                ["{}: {} missing".format(p, q) for p, q in errors.items()]
            )
            raise exceptions.ValidationError(
                _("Missing products:\n{}").format(error_string)
            )

    def _get_origin_mo(self):
        finished_move_lines = self.env["stock.move.line"].search(
            [
                ("product_id", "=", self.unbuild_product_id.id),
                ("lot_id", "=", self.unbuild_lot_id.id),
            ]
        )
        manufacturing_orders = finished_move_lines.mapped("production_id")
        origin_manufacturing_order = self.env["mrp.production"].search(
            [("id", "in", manufacturing_orders.ids), ],
            order="date_finished desc",
            limit=1,
        )
        if not origin_manufacturing_order:
            raise exceptions.ValidationError(
                _("No matching manufacturing order found for lot {}").format(
                    self.unbuild_lot_id.name
                )
            )
        return origin_manufacturing_order

    def _dismantle(self, origin_manufacturing_order):
        unbuild_order = self.env["mrp.unbuild"].create(
            {
                "product_id": self.unbuild_product_id.id,
                "product_uom_id": self.unbuild_product_id.uom_id.id,
                "bom_id": self.unbuild_bom_id.id,
                "mo_id": origin_manufacturing_order.id,
                "lot_id": self.unbuild_lot_id.id,
            }
        )
        unbuild_order.action_validate()
        return unbuild_order

    def _rebuild(self, origin_manufacturing_order):
        rebuild_order = self.env["mrp.production"].create(
            {
                "product_id": self.rebuild_product_id.id,
                "product_uom_id": self.rebuild_product_id.uom_id.id,
                "bom_id": self.rebuild_bom_id.id,
                "product_qty": self.quantity,
            }
        )
        rebuild_order.action_assign()
        produce_wizard = (
            self.env["mrp.product.produce"]
            .with_context(active_id=rebuild_order.id)
            .create({})
        )
        if not self.rebuild_lot_id:
            self.rebuild_lot_id = self.env["stock.production.lot"].create(
                {
                    "name": self.unbuild_lot_id.name,
                    "product_id": self.rebuild_product_id.id,
                }
            )
        produce_wizard.lot_id = self.rebuild_lot_id
        produce_wizard._onchange_product_qty()

        # Assign previous components lots
        unbuilt_raw_moves = origin_manufacturing_order.move_raw_ids
        rebuilt_produce_lines = produce_wizard.produce_line_ids
        self._assign_previous_lots(unbuilt_raw_moves, rebuilt_produce_lines)

        produce_wizard.do_produce()
        rebuild_order.button_mark_done()
        return rebuild_order

    def _assign_previous_lots(self, unbuilt_raw_moves, rebuilt_produce_lines):
        for line in rebuilt_produce_lines:
            unbuilt_raw_move = unbuilt_raw_moves.filtered(
                lambda m: m.product_id == line.product_id
            )
            if unbuilt_raw_move:
                unbuilt_move_line = unbuilt_raw_move.active_move_line_ids
                unbuilt_move_line.ensure_one()
                line.lot_id = unbuilt_move_line.lot_id
                unbuilt_raw_moves -= unbuilt_raw_move

    def process(self):
        self.ensure_one()
        self._check_dismatled_contains_components()
        self._check_availability()

        # Get manufacturing order for product to be unbuilt
        origin_manufacturing_order = self._get_origin_mo()

        # Dismantling
        unbuild_order = self._dismantle(origin_manufacturing_order)

        # Assembly
        rebuild_order = self._rebuild(origin_manufacturing_order)

        self.write(
            {
                "state": "done",
                "unbuild_order_id": unbuild_order.id,
                "rebuild_order_id": rebuild_order.id,
            }
        )
