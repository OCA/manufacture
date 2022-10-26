# Copyright 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# Copyright 2016-19 ForgeFlow S.L. (https://www.forgeflow.com)
# - Jordi Ballester Alomar <jordi.ballester@forgeflow.com>
# - Lois Rilo Antelo <lois.rilo@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from math import ceil

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ProductMRPArea(models.Model):
    _name = "product.mrp.area"
    _description = "Product MRP Area"

    active = fields.Boolean(default=True)
    mrp_area_id = fields.Many2one(comodel_name="mrp.area", required=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="mrp_area_id.warehouse_id.company_id",
        store=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product", required=True, string="Product"
    )
    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        readonly=True,
        related="product_id.product_tmpl_id",
        store=True,
    )
    location_id = fields.Many2one(related="mrp_area_id.location_id")
    location_proc_id = fields.Many2one(
        string="Procure Location",
        comodel_name="stock.location",
        domain="[('location_id', 'child_of', location_id)]",
        help="Set this if you need to procure from a different location"
        "than area's location.",
    )
    # TODO: applicable and exclude... redundant??
    mrp_applicable = fields.Boolean(string="MRP Applicable")
    mrp_exclude = fields.Boolean(string="Exclude from MRP")
    mrp_inspection_delay = fields.Integer(string="Inspection Delay")
    mrp_maximum_order_qty = fields.Float(string="Maximum Order Qty", default=0.0)
    mrp_minimum_order_qty = fields.Float(string="Minimum Order Qty", default=0.0)
    mrp_minimum_stock = fields.Float(string="Safety Stock")
    mrp_nbr_days = fields.Integer(
        string="Nbr. Days",
        default=0,
        help="Number of days to group demand for this product during the "
        "MRP run, in order to determine the quantity to order.",
    )
    mrp_qty_multiple = fields.Float(string="Qty Multiple", default=1.00)
    mrp_transit_delay = fields.Integer(string="Transit Delay", default=0)
    mrp_verified = fields.Boolean(
        string="Verified for MRP",
        help="Identifies that this product has been verified "
        "to be valid for the MRP.",
    )
    mrp_lead_time = fields.Float(string="Lead Time", compute="_compute_mrp_lead_time")
    main_supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Main Supplier",
        compute="_compute_main_supplier",
        store=True,
        index=True,
    )
    main_supplierinfo_id = fields.Many2one(
        comodel_name="product.supplierinfo",
        string="Supplier Info",
        compute="_compute_main_supplier",
        store=True,
    )
    supply_method = fields.Selection(
        selection=[
            ("buy", "Buy"),
            ("none", "Undefined"),
            ("manufacture", "Produce"),
            ("phantom", "Kit"),
            ("pull", "Pull From"),
            ("push", "Push To"),
            ("pull_push", "Pull & Push"),
        ],
        string="Supply Method",
        compute="_compute_supply_method",
    )
    qty_available = fields.Float(
        string="Quantity Available", compute="_compute_qty_available"
    )
    mrp_move_ids = fields.One2many(
        comodel_name="mrp.move", inverse_name="product_mrp_area_id", readonly=True
    )
    planned_order_ids = fields.One2many(
        comodel_name="mrp.planned.order",
        inverse_name="product_mrp_area_id",
        readonly=True,
    )

    _sql_constraints = [
        (
            "product_mrp_area_uniq",
            "unique(product_id, mrp_area_id)",
            "The product/MRP Area parameters combination must be unique.",
        )
    ]

    @api.constrains(
        "mrp_minimum_order_qty",
        "mrp_maximum_order_qty",
        "mrp_qty_multiple",
        "mrp_minimum_stock",
        "mrp_nbr_days",
    )
    def _check_negatives(self):
        values = self.read(
            [
                "mrp_minimum_order_qty",
                "mrp_maximum_order_qty",
                "mrp_qty_multiple",
                "mrp_minimum_stock",
                "mrp_nbr_days",
            ]
        )
        for rec in values:
            if any(v < 0 for v in rec.values()):
                raise ValidationError(_("You cannot use a negative number."))

    def name_get(self):
        return [
            (
                area.id,
                "[{}] {}".format(area.mrp_area_id.name, area.product_id.display_name),
            )
            for area in self
        ]

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        if operator in ("ilike", "like", "=", "=like", "=ilike"):
            args = expression.AND(
                [
                    args or [],
                    [
                        "|",
                        "|",
                        ("product_id.name", operator, name),
                        ("product_id.default_code", operator, name),
                        ("mrp_area_id.name", operator, name),
                    ],
                ]
            )
        return super(ProductMRPArea, self)._name_search(
            name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid
        )

    def _compute_mrp_lead_time(self):
        produced = self.filtered(lambda r: r.supply_method == "manufacture")
        purchased = self.filtered(lambda r: r.supply_method == "buy")
        for rec in produced:
            rec.mrp_lead_time = rec.product_id.produce_delay
        for rec in purchased:
            rec.mrp_lead_time = rec.main_supplierinfo_id.delay
        # TODO: 'move' supply method.
        for rec in self - produced - purchased:
            rec.mrp_lead_time = 0

    def _compute_qty_available(self):
        for rec in self:
            rec.qty_available = rec.product_id.with_context(
                {"location": rec.mrp_area_id.location_id.id}
            ).qty_available

    def _compute_supply_method(self):
        group_obj = self.env["procurement.group"]
        for rec in self:
            proc_loc = rec.location_proc_id or rec.mrp_area_id.location_id
            values = {
                "warehouse_id": rec.mrp_area_id.warehouse_id,
                "company_id": rec.mrp_area_id.company_id,
            }
            rule = group_obj._get_rule(rec.product_id, proc_loc, values)
            if (
                rule.action == "manufacture"
                and rec.product_id.product_tmpl_id.bom_ids
                and rec.product_id.product_tmpl_id.bom_ids[0].type == "phantom"
            ):
                rec.supply_method = "phantom"
            else:
                rec.supply_method = rule.action if rule else "none"

    @api.depends(
        "mrp_area_id", "supply_method", "product_id.route_ids", "product_id.seller_ids"
    )
    def _compute_main_supplier(self):
        """Simplified and similar to procurement.rule logic."""
        for rec in self.filtered(lambda r: r.supply_method == "buy"):
            suppliers = rec.product_id.seller_ids.filtered(
                lambda r: (not r.product_id or r.product_id == rec.product_id)
                and (not r.company_id or r.company_id == rec.company_id)
            )
            if not suppliers:
                rec.main_supplierinfo_id = False
                rec.main_supplier_id = False
                continue
            rec.main_supplierinfo_id = suppliers[0]
            rec.main_supplier_id = suppliers[0].name
        for rec in self.filtered(lambda r: r.supply_method != "buy"):
            rec.main_supplierinfo_id = False
            rec.main_supplier_id = False

    def _adjust_qty_to_order(self, qty_to_order):
        self.ensure_one()
        if (
            not self.mrp_maximum_order_qty
            and not self.mrp_minimum_order_qty
            and self.mrp_qty_multiple == 1.0
        ):
            return qty_to_order
        if qty_to_order < self.mrp_minimum_order_qty:
            return self.mrp_minimum_order_qty
        if self.mrp_qty_multiple:
            multiplier = ceil(qty_to_order / self.mrp_qty_multiple)
            qty_to_order = multiplier * self.mrp_qty_multiple
        if self.mrp_maximum_order_qty and qty_to_order > self.mrp_maximum_order_qty:
            return self.mrp_maximum_order_qty
        return qty_to_order

    def update_min_qty_from_main_supplier(self):
        for rec in self.filtered(
            lambda r: r.main_supplierinfo_id and r.supply_method == "buy"
        ):
            rec.mrp_minimum_order_qty = rec.main_supplierinfo_id.min_qty

    def _in_stock_moves_domain(self):
        self.ensure_one()
        locations = self.mrp_area_id._get_locations()
        return [
            ("product_id", "=", self.product_id.id),
            ("state", "not in", ["done", "cancel"]),
            ("product_qty", ">", 0.00),
            ("location_id", "not in", locations.ids),
            ("location_dest_id", "in", locations.ids),
        ]

    def _out_stock_moves_domain(self):
        self.ensure_one()
        locations = self.mrp_area_id._get_locations()
        return [
            ("product_id", "=", self.product_id.id),
            ("state", "not in", ["done", "cancel"]),
            ("product_qty", ">", 0.00),
            ("location_id", "in", locations.ids),
            ("location_dest_id", "not in", locations.ids),
        ]

    def action_view_stock_moves(self, domain):
        self.ensure_one()
        xmlid = "stock.stock_move_action"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action["domain"] = domain
        action["context"] = {}
        return action

    def action_view_incoming_stock_moves(self):
        return self.action_view_stock_moves(self._in_stock_moves_domain())

    def action_view_outgoing_stock_moves(self):
        return self.action_view_stock_moves(self._out_stock_moves_domain())

    def _to_be_exploded(self):
        self.ensure_one()
        return self.supply_method in ["manufacture", "phantom"]
