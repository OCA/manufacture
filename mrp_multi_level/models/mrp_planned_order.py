# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# - Lois Rilo Antelo <lois.rilo@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from datetime import timedelta

from odoo import api, fields, models


class MrpPlannedOrder(models.Model):
    _name = "mrp.planned.order"
    _description = "Planned Order"
    _order = "due_date, id"

    name = fields.Char(string="Description")
    product_mrp_area_id = fields.Many2one(
        comodel_name="product.mrp.area",
        string="Product MRP Area",
        index=True,
        required=True,
        ondelete="cascade",
    )
    mrp_area_id = fields.Many2one(
        comodel_name="mrp.area",
        related="product_mrp_area_id.mrp_area_id",
        string="MRP Area",
        store=True,
        index=True,
        readonly=True,
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
        readonly=True,
    )
    order_release_date = fields.Date(
        string="Release Date", help="Order release date planned by MRP.", required=True
    )
    due_date = fields.Date(
        string="Due Date",
        help="Date in which the supply must have been completed.",
        required=True,
    )
    qty_released = fields.Float(readonly=True)
    fixed = fields.Boolean(default=True)
    mrp_qty = fields.Float(string="Quantity")
    mrp_move_down_ids = fields.Many2many(
        comodel_name="mrp.move",
        relation="mrp_move_planned_order_rel",
        column1="order_id",
        column2="move_down_id",
        string="MRP Move DOWN",
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
        string="Action",
    )
    mrp_inventory_id = fields.Many2one(
        string="Associated MRP Inventory",
        comodel_name="mrp.inventory",
        ondelete="set null",
    )
    mrp_production_ids = fields.One2many(
        "mrp.production", "planned_order_id", string="Manufacturing Orders"
    )
    mo_count = fields.Integer(compute="_compute_mrp_production_count")

    def _compute_mrp_production_count(self):
        for rec in self:
            rec.mo_count = len(rec.mrp_production_ids)

    @api.onchange("due_date")
    def _onchange_due_date(self):
        if self.due_date:
            if self.product_mrp_area_id.mrp_lead_time:
                calendar = self.mrp_area_id.calendar_id
                if calendar:
                    dt = fields.Datetime.from_string(self.due_date)
                    res = calendar.plan_days(
                        -1 * (self.product_mrp_area_id.mrp_lead_time + 1), dt
                    )
                    self.order_release_date = res.date()
                else:
                    self.order_release_date = fields.Date.from_string(
                        self.due_date
                    ) - timedelta(days=self.product_mrp_area_id.mrp_lead_time)

    def action_toggle_fixed(self):
        for rec in self:
            rec.fixed = not rec.fixed

    def action_open_linked_mrp_production(self):
        xmlid = "mrp.mrp_production_action"
        result = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        result["context"] = {}
        result["domain"] = "[('id','in',%s)]" % self.mrp_production_ids.ids
        return result
