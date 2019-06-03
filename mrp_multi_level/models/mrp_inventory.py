# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# Copyright 2016-19 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar <jordi.ballester@eficent.com>
# - Lois Rilo Antelo <lois.rilo@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from datetime import timedelta, date


class MrpInventory(models.Model):
    _name = 'mrp.inventory'
    _order = 'product_mrp_area_id, date'
    _description = 'MRP inventory projections'
    _rec_name = 'product_mrp_area_id'

    # TODO: name to pass to procurements?
    # TODO: compute procurement_date to pass to the wizard? not needed for
    # PO at least. Check for MO and moves

    mrp_area_id = fields.Many2one(
        comodel_name='mrp.area', string='MRP Area',
        related='product_mrp_area_id.mrp_area_id', store=True,
    )
    product_mrp_area_id = fields.Many2one(
        comodel_name='product.mrp.area', string='Product Parameters',
        index=True,
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        related='product_mrp_area_id.product_id',
        store=True,
    )
    uom_id = fields.Many2one(
        comodel_name='product.uom', string='Product UoM',
        compute='_compute_uom_id',
    )
    date = fields.Date(string='Date')
    demand_qty = fields.Float(string='Demand')
    supply_qty = fields.Float(string='Supply')
    initial_on_hand_qty = fields.Float(string='Starting Inventory')
    final_on_hand_qty = fields.Float(string='Forecasted Inventory')
    to_procure = fields.Float(
        string="To procure",
        compute="_compute_to_procure",
        store=True,
    )
    running_availability = fields.Float(
        string="Planned Availability",
        help="Theoretical inventory level if all planned orders"
             "were released.",
    )
    order_release_date = fields.Date(
        string="Order Release Date",
        compute="_compute_order_release_date",
        store=True,
    )
    planned_order_ids = fields.One2many(
        comodel_name="mrp.planned.order",
        inverse_name="mrp_inventory_id",
        readonly=True,
    )

    @api.multi
    def _compute_uom_id(self):
        for rec in self:
            rec.uom_id = rec.product_mrp_area_id.product_id.uom_id

    @api.depends("planned_order_ids", "planned_order_ids.qty_released")
    def _compute_to_procure(self):
        for rec in self:
            rec.to_procure = sum(rec.planned_order_ids.mapped('mrp_qty')) - \
                sum(rec.planned_order_ids.mapped('qty_released'))

    @api.multi
    @api.depends('product_mrp_area_id',
                 'product_mrp_area_id.main_supplierinfo_id',
                 'product_mrp_area_id.mrp_lead_time',
                 'product_mrp_area_id.mrp_area_id.calendar_id')
    def _compute_order_release_date(self):
        today = date.today()
        for rec in self.filtered(lambda r: r.date):
            delay = rec.product_mrp_area_id.mrp_lead_time
            if delay and rec.mrp_area_id.calendar_id:
                dt_date = fields.Datetime.from_string(rec.date)
                order_release_date = rec.mrp_area_id.calendar_id.plan_days(
                    -delay - 1, dt_date).date()
            else:
                order_release_date = fields.Date.from_string(
                    rec.date) - timedelta(days=delay)
            if order_release_date < today:
                order_release_date = today
            rec.order_release_date = order_release_date
