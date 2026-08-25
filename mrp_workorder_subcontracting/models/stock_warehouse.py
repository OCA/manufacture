from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    sub_out_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Subcontract Picking Type OUT",
        copy=False,
    )
    sub_in_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Subcontract Picking Type IN",
        copy=False,
    )
    sub_out_virtual_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Subcontract Virtual Picking Type OUT",
        copy=False,
    )
    sub_in_virtual_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Subcontract Virtual Picking Type IN",
        copy=False,
    )
