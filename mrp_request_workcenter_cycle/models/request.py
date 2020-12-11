# Copyright 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from math import floor

from odoo import _, api, fields, models
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp


class MrpProductionRequest(models.Model):
    _inherit = "mrp.production.request"

    qty_by_workcenter_ids = fields.One2many(
        comodel_name="mrp.request.workcenter",
        inverse_name="request_id",
        string="Workcenters cycles number",
    )
    workcenter_lines_count = fields.Integer(
        compute="_compute_workcenter_lines_count",
        help="Technical field: size of qty_by_workcenter_ids field",
    )
    auto_product_qty = fields.Float(
        compute="_compute_auto_product_qty",
        store=True,
        compute_sudo=True,
        digits=dp.get_precision("Product Unit of Measure"),
    )
    target_quantity = fields.Float(
        digits=dp.get_precision("Product Unit of Measure"),
        help="This is your initial quantity defined before any cycle adjustement.",
    )

    @api.depends("qty_by_workcenter_ids")
    def _compute_auto_product_qty(self):
        for rec in self:
            if rec.qty_by_workcenter_ids:
                if rec.product_uom_id and rec.product_uom_id != rec.product_id.uom_id:
                    raise UserError(
                        _(
                            "Computing quantity with different units is "
                            "not supported for now."
                        )
                    )
                qty = 0
                for qty_by in rec.qty_by_workcenter_ids:
                    qty += qty_by.product_qty * qty_by.workcenter_cycle_no
                rec.auto_product_qty = qty
                # need sudo to write in a not computed field in computed method
                rec.sudo().write({"product_qty": qty})
            else:
                rec.auto_product_qty = 0

    @api.onchange("product_id")
    def _onchange_product_id(self):
        super()._onchange_product_id()
        self.populate_qty_by_workcenter()

    @api.onchange("target_quantity")
    def _onchange_target_quantity(self):
        self.populate_qty_by_workcenter()

    def populate_qty_by_workcenter(self):
        for rec in self:
            cycle_factor = 1
            if rec.target_quantity and rec.product_id.qty_by_workcenter_ids:
                # this factor allow us to compute the total quantity
                # allocated by machine
                cycle_factor = rec.target_quantity / sum(
                    x.product_qty * x.workcenter_cycle_no
                    for x in rec.product_id.qty_by_workcenter_ids
                )
            rec.qty_by_workcenter_ids = [(5, 0, 0)]
            rec.qty_by_workcenter_ids = [
                (
                    0,
                    0,
                    {
                        "workcenter_cycle_no": x.workcenter_cycle_no * cycle_factor,
                        "workcenter_id": x.workcenter_id.id,
                        "request_id": rec.id,
                        "product_qty": x.product_qty,
                    },
                )
                for x in rec.product_id.qty_by_workcenter_ids
            ]

    def _compute_workcenter_lines_count(self):
        for rec in self:
            rec.workcenter_lines_count = len(rec.qty_by_workcenter_ids)

    def button_create_mo_by_workcenter(self):
        for rec in self:
            if rec.mrp_production_ids:
                raise UserError(_("MO already exists"))
            if rec.qty_by_workcenter_ids:
                for qty_by in rec.qty_by_workcenter_ids:
                    qty = floor(qty_by.workcenter_cycle_no)
                    while qty:
                        mo_qty = qty_by.product_qty
                        self._get_mo_from_request(mo_qty, qty_by.workcenter_id)
                        qty -= 1
                    rest = qty_by.workcenter_cycle_no - floor(
                        qty_by.workcenter_cycle_no
                    )
                    if rest:
                        mo_qty = qty_by.product_qty * rest
                        self._get_mo_from_request(mo_qty, qty_by.workcenter_id)

    @api.model
    def _get_mo_from_request(self, mo_qty, workcenter):
        wiz = (
            self.env["mrp.production.request.create.mo"]
            .with_context(active_ids=[self.id], active_model="mrp.production.request")
            .create({})
        )
        wiz.compute_product_line_ids()
        wiz.mo_qty = mo_qty
        wiz.product_uom_id = self.product_id.uom_id.id
        wiz.with_context(workcenter=workcenter.name).create_mo()
