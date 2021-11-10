# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
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
        return {
            "planned_order_id": planned_order.id,
            "qty": planned_order.mrp_qty - planned_order.qty_released,
            "uom_id": planned_order.mrp_inventory_id.uom_id.id,
            "date_planned": planned_order.due_date,
            "mrp_inventory_id": planned_order.mrp_inventory_id.id,
            "product_id": planned_order.product_id.id,
            "warehouse_id": planned_order.mrp_area_id.warehouse_id.id,
            "location_id": planned_order.product_mrp_area_id.location_proc_id.id
            or planned_order.mrp_area_id.location_id.id,
            "supply_method": planned_order.product_mrp_area_id.supply_method,
        }

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        if self.user_has_groups("mrp_multi_level.group_change_mrp_procure_qty"):
            view_id = self.env.ref(
                "mrp_multi_level." "view_mrp_inventory_procure_wizard"
            ).id
        else:
            view_id = self.env.ref(
                "mrp_multi_level." "view_mrp_inventory_procure_without_security"
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
                if line.qty_released < line.mrp_qty:
                    items += item_obj.create(self._prepare_item(line))
        if items:
            res["item_ids"] = [(6, 0, items.ids)]
        return res

    def make_procurement(self):
        self.ensure_one()
        errors = []
        pg = self.env["procurement.group"]
        procurements = []
        for item in self.item_ids:
            if not item.qty:
                raise ValidationError(_("Quantity must be positive."))
            values = item._prepare_procurement_values()
            procurements.append(
                pg.Procurement(
                    item.product_id,
                    item.qty,
                    item.uom_id,
                    item.location_id,
                    "MRP: " + str(self.env.user.login),  # name?
                    "MRP: " + str(self.env.user.login),  # origin?
                    item.mrp_inventory_id.company_id,
                    values,
                )
            )
        # Run procurements
        try:
            pg.run(procurements)
            for item in self.item_ids:
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
        string="Supply Method",
        selection=[
            ("buy", "Buy"),
            ("none", "Undefined"),
            ("manufacture", "Produce"),
            ("pull", "Pull From"),
            ("push", "Push To"),
            ("pull_push", "Pull & Push"),
        ],
        readonly=True,
    )

    def _prepare_procurement_values(self, group=False):
        return {
            "date_planned": fields.Datetime.to_string(
                fields.Date.from_string(self.date_planned)
            ),
            "warehouse_id": self.warehouse_id,
            "group_id": group,
            "planned_order_id": self.planned_order_id.id,
        }

    @api.onchange("uom_id")
    def onchange_uom_id(self):
        for rec in self:
            rec.qty = rec.mrp_inventory_id.uom_id._compute_quantity(
                rec.mrp_inventory_id.to_procure, rec.uom_id
            )
