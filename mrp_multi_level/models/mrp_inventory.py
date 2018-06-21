# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# Copyright 2016-18 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar <jordi.ballester@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpInventory(models.Model):
    _name = 'mrp.inventory'
    _order = 'mrp_product_id, date'
    _description = 'MRP inventory projections'
    _rec_name = 'mrp_product_id'

    # TODO: uom??
    # TODO: name to pass to procurements?
    # TODO: compute procurement_date to pass to the wizard? not needed for PO at least. Check for MO and moves
    # TODO: substract qty already procured.
    # TODO: show a LT based on the procure method?
    # TODO: add to_procure_date

    mrp_area_id = fields.Many2one(
        comodel_name='mrp.area', string='MRP Area',
        related='mrp_product_id.mrp_area_id',
    )
    mrp_product_id = fields.Many2one(
        comodel_name='mrp.product', string='Product',
        index=True,
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
    to_procure = fields.Float(string='To procure')

    @api.multi
    def _compute_uom_id(self):
        for rec in self:
            rec.uom_id = rec.mrp_product_id.product_id.uom_id
