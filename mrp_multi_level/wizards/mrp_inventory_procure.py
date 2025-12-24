# Copyright 2018-21 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class MrpInventoryProcure(models.TransientModel):
    _name = "mrp.inventory.procure"
    _description = "Make Procurements from MRP inventory projections"

    item_ids = fields.One2many(
        comodel_name="mrp.inventory.procure.item", inverse_name="wiz_id", string="Items"
    )

    @api.model
    def _prepare_item(self, planned_order):
        active_model = self.env.context.get("active_model", "mrp.inventory")
        source_context = (
            "planned_order" if active_model == "mrp.planned.order" else "inventory"
        )
        qty_pending = planned_order.mrp_qty - planned_order.qty_released
        return {
            "planned_order_id": planned_order.id,
            "qty": qty_pending,
            "uom_id": planned_order.mrp_inventory_id.uom_id.id,
            "date_planned": planned_order.due_date,
            "mrp_inventory_id": planned_order.mrp_inventory_id.id,
            "product_id": planned_order.product_id.id,
            "warehouse_id": planned_order.mrp_area_id.warehouse_id.id,
            "location_id": planned_order.product_mrp_area_id.location_proc_id.id
            or planned_order.mrp_area_id.location_id.id,
            "supply_method": planned_order.product_mrp_area_id.supply_method,
            "mrp_action": planned_order.mrp_action
            or planned_order.product_mrp_area_id.supply_method,
            "original_qty": qty_pending,
            "source_context": source_context,
        }

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        if self.user_has_groups("mrp_multi_level.group_change_mrp_procure_qty"):
            view_id = self.env.ref(
                "mrp_multi_level.view_mrp_inventory_procure_wizard"
            ).id
        else:
            view_id = self.env.ref(
                "mrp_multi_level.view_mrp_inventory_procure_without_security"
            ).id
        return super(MrpInventoryProcure, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )

    @api.model
    def default_get(self, fields):
        res = super(MrpInventoryProcure, self).default_get(fields)
        active_ids = self.env.context["active_ids"] or []
        active_model = self.env.context["active_model"]
        if not active_ids or "item_ids" not in fields:
            return res
        items = item_obj = self.env["mrp.inventory.procure.item"]
        if active_model == "mrp.inventory":
            mrp_inventory_obj = self.env[active_model]
            for line in mrp_inventory_obj.browse(active_ids).mapped(
                "planned_order_ids"
            ):
                if line.qty_released < line.mrp_qty:
                    items += item_obj.create(self._prepare_item(line))
        elif active_model == "mrp.planned.order":
            mrp_planned_order_obj = self.env[active_model]
            for line in mrp_planned_order_obj.browse(active_ids):
                if line.mrp_action == "phantom":
                    continue
                if line.qty_released < line.mrp_qty:
                    items += item_obj.create(self._prepare_item(line))
        if items:
            res["item_ids"] = [(6, 0, items.ids)]
        return res

    def make_procurement(self):
        self.ensure_one()
        errors = []
        pg = self.env["procurement.group"]
        for item in self.item_ids:
            if not item.qty:
                raise ValidationError(_("Quantity must be positive."))
            if not item.uom_id:
                item.uom_id = item.product_id.uom_id
            if not item.uom_id.rounding or item.uom_id.rounding <= 0:
                raise ValidationError(
                    _(
                        "The Unit of Measure '%(uom)s' has an invalid rounding (%(rounding)s). "
                        "Please fix the UoM configuration (rounding must be > 0)."
                    )
                    % {
                        "uom": item.uom_id.display_name,
                        "rounding": item.uom_id.rounding,
                    }
                )

            values = item._prepare_procurement_values()
            company = (
                item.mrp_inventory_id.company_id
                or item.warehouse_id.company_id
                or self.env.company
            )
            values["company_id"] = company

            procurement = pg.Procurement(
                item.product_id,
                item.qty,
                item.uom_id,
                item.location_id,
                "MRP: " + (item.planned_order_id.name or self.env.user.login),
                "MRP: " + (item.planned_order_id.origin or self.env.user.login),
                company,
                values,
            )

            try:
                pg.run([procurement])
                item.planned_order_id.qty_released += item.qty
            except UserError as error:
                errors.append(error.name)

        if errors:
            raise UserError("\n".join(errors))
        return {"type": "ir.actions.act_window_close"}


class MrpInventoryProcureItem(models.TransientModel):
    _name = "mrp.inventory.procure.item"
    _description = "MRP Inventory procure item"

    wiz_id = fields.Many2one(
        comodel_name="mrp.inventory.procure",
        string="Wizard",
        ondelete="cascade",
        readonly=True,
    )
    qty = fields.Float(string="Quantity")
    uom_id = fields.Many2one(string="Unit of Measure", comodel_name="uom.uom")
    date_planned = fields.Date(string="Planned Date", required=True)
    mrp_inventory_id = fields.Many2one(
        string="Mrp Inventory", comodel_name="mrp.inventory"
    )
    planned_order_id = fields.Many2one(comodel_name="mrp.planned.order")
    product_id = fields.Many2one(string="Product", comodel_name="product.product")
    warehouse_id = fields.Many2one(string="Warehouse", comodel_name="stock.warehouse")
    location_id = fields.Many2one(string="Location", comodel_name="stock.location")
    supply_method = fields.Selection(
        selection=[
            ("buy", "Buy"),
            ("none", "Undefined"),
            ("manufacture", "Produce"),
            ("pull", "Pull From"),
            ("push", "Push To"),
            ("pull_push", "Pull & Push"),
        ],
        readonly=True,
        string="Default Supply Method",
        help=(
            "Default supply strategy derived from routes/stock rules for the product/area. "
            "It will be used when creating procurements if the procurement method is not "
            "explicitly specified."
        ),
    )
    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Vendor",
        help="Vendor selected from the product's vendor list (seller info).",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        help="Currency that will be used for a purchase procurement.",
    )
    original_qty = fields.Float(
        string="Original Planned Qty",
        help="Original quantity from planned order, used as reference",
        readonly=True,
    )
    source_context = fields.Selection(
        selection=[
            ("inventory", "From Inventory"),
            ("planned_order", "From Planned Order"),
        ],
        default="inventory",
        readonly=True,
    )
    mrp_action = fields.Selection(
        selection=[
            ("manufacture", "Manufacturing Order"),
            ("buy", "Purchase Order"),
            ("pull", "Pull From"),
            ("push", "Push To"),
            ("pull_push", "Pull & Push"),
            ("none", "None"),
        ],
        string="Procurement Method",
        help="Method to use for procurement. Can be modified before executing.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.mrp_action == "buy" and rec.product_id and rec.warehouse_id:
                rec._onchange_purchase_defaults()
        return records

    @api.onchange(
        "product_id", "warehouse_id", "qty", "uom_id", "date_planned", "mrp_action"
    )
    def _onchange_purchase_defaults(self):
        """Pre-fill vendor/currency for buy procurements so the user can see them."""
        for rec in self:
            if rec.mrp_action != "buy" or not rec.product_id or not rec.warehouse_id:
                rec.supplier_id = False
                rec.currency_id = False
                continue

            company = rec.warehouse_id.company_id or rec.env.company
            qty = rec.qty or 0.0
            uom = rec.uom_id or rec.product_id.uom_id

            seller = rec.product_id._select_seller(
                quantity=qty,
                date=rec.date_planned,
                uom_id=uom,
                partner_id=False,
            )
            if not seller:
                seller = rec.product_id.seller_ids.filtered(
                    lambda s: (not s.company_id or s.company_id == company)
                ).sorted(lambda s: (s.sequence, s.min_qty, s.price))[:1]

            rec.supplier_id = seller.partner_id if seller else False
            rec.currency_id = (
                seller.currency_id
                if (seller and seller.currency_id)
                else company.currency_id
            )

    def _prepare_procurement_values(self, group=False):
        company = self.warehouse_id.company_id or self.env.company
        currency = company.currency_id
        res = {
            "date_planned": self.date_planned,
            "warehouse_id": self.warehouse_id,
            "group_id": group,
            "planned_order_id": self.planned_order_id.id,
            "company_id": company,
            "currency_id": currency.id,
        }
        if self.mrp_action:
            res["mrp_action"] = self.mrp_action
        should_add_supplier = (self.mrp_action == "buy") or (
            not self.mrp_action and self.supply_method == "buy"
        )
        if should_add_supplier:
            qty = self.qty or 0.0
            uom = self.uom_id or self.product_id.uom_id
            supplier_info = self.product_id._select_seller(
                quantity=qty,
                date=self.date_planned,
                uom_id=uom,
                partner_id=self.supplier_id,
            )
            if not supplier_info:
                supplier_info = self.product_id.seller_ids.filtered(
                    lambda s: (not s.company_id or s.company_id == company)
                ).sorted(lambda s: (s.sequence, s.min_qty, s.price))[:1]
            if supplier_info:
                res["supplierinfo_id"] = supplier_info
                res["currency_id"] = (
                    supplier_info.currency_id or company.currency_id
                ).id
            else:
                res["currency_id"] = company.currency_id.id
        return res

    @api.onchange("uom_id")
    def onchange_uom_id(self):
        for rec in self:
            if rec.source_context == "planned_order":
                if rec.original_qty and rec.uom_id:
                    product_uom = rec.product_id.uom_id
                    rec.qty = product_uom._compute_quantity(
                        rec.original_qty, rec.uom_id
                    )
                continue

            if rec.mrp_inventory_id and rec.mrp_inventory_id.to_procure > 0:
                rec.qty = rec.mrp_inventory_id.uom_id._compute_quantity(
                    rec.mrp_inventory_id.to_procure, rec.uom_id
                )
            elif rec.original_qty:
                product_uom = rec.product_id.uom_id
                rec.qty = product_uom._compute_quantity(rec.original_qty, rec.uom_id)
