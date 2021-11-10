# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# Copyright 2016-21 ForgeFlow S.L. (https://www.forgeflow.com)
# - Jordi Ballester Alomar <jordi.ballester@forgeflow.com>
# - Lois Rilo Antelo <lois.rilo@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import date, timedelta

from odoo import api, fields, models


class MrpInventory(models.Model):
    _name = "mrp.inventory"
    _order = "product_mrp_area_id, date"
    _description = "MRP inventory projections"
    _rec_name = "product_mrp_area_id"

    # TODO: name to pass to procurements?
    # TODO: compute procurement_date to pass to the wizard? not needed for
    # PO at least. Check for MO and moves

    mrp_area_id = fields.Many2one(
        comodel_name="mrp.area",
        string="MRP Area",
        related="product_mrp_area_id.mrp_area_id",
        store=True,
    )
    product_mrp_area_id = fields.Many2one(
        comodel_name="product.mrp.area",
        string="Product Parameters",
        index=True,
        required=True,
        ondelete="cascade",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="product_mrp_area_id.mrp_area_id.warehouse_id.company_id",
        store=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="product_mrp_area_id.product_id",
        store=True,
    )
    uom_id = fields.Many2one(
        comodel_name="uom.uom", string="Product UoM", compute="_compute_uom_id"
    )
    date = fields.Date(string="Date")
    demand_qty = fields.Float(string="Demand")
    supply_qty = fields.Float(string="Supply")
    initial_on_hand_qty = fields.Float(string="Starting Inventory")
    final_on_hand_qty = fields.Float(string="Forecasted Inventory")
    to_procure = fields.Float(
        string="To procure", compute="_compute_to_procure", store=True
    )
    running_availability = fields.Float(
        string="Planned Availability",
        help="Theoretical inventory level if all planned orders" "were released.",
    )
    order_release_date = fields.Date(
        string="Order Release Date", compute="_compute_order_release_date", store=True
    )
    planned_order_ids = fields.One2many(
        comodel_name="mrp.planned.order", inverse_name="mrp_inventory_id", readonly=True
    )
    supply_method = fields.Selection(
        string="Supply Method",
        related="product_mrp_area_id.supply_method",
        readonly=True,
        store=True,
    )
    main_supplier_id = fields.Many2one(
        string="Main Supplier",
        related="product_mrp_area_id.main_supplier_id",
        readonly=True,
        store=True,
    )

    def _compute_uom_id(self):
        for rec in self:
            rec.uom_id = rec.product_mrp_area_id.product_id.uom_id

    @api.depends("planned_order_ids", "planned_order_ids.qty_released")
    def _compute_to_procure(self):
        for rec in self:
            rec.to_procure = sum(rec.planned_order_ids.mapped("mrp_qty")) - sum(
                rec.planned_order_ids.mapped("qty_released")
            )

    @api.depends(
        "product_mrp_area_id",
        "product_mrp_area_id.main_supplierinfo_id",
        "product_mrp_area_id.mrp_lead_time",
        "product_mrp_area_id.mrp_area_id.calendar_id",
    )
    def _compute_order_release_date(self):
        today = date.today()
        for rec in self.filtered(lambda r: r.date):
            delay = rec.product_mrp_area_id.mrp_lead_time
            if delay and rec.mrp_area_id.calendar_id:
                dt_date = fields.Datetime.to_datetime(rec.date)
                # dt_date is at the beginning of the day (00:00),
                # so we can subtract the delay straight forward.
                order_release_date = rec.mrp_area_id.calendar_id.plan_days(
                    -delay, dt_date
                ).date()
            elif delay:
                order_release_date = fields.Date.from_string(rec.date) - timedelta(
                    days=delay
                )
            else:
                order_release_date = rec.date
            if order_release_date < today:
                order_release_date = today
            rec.order_release_date = order_release_date
