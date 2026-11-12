from odoo import fields, models


class PurchaseOrderType(models.Model):
    _inherit = "purchase.order.type"

    is_subcontracting = fields.Boolean(string="Is a subcontracting type", default=False)
    sub_out_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type", string="Subcontract Picking Type OUT"
    )
    sub_in_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type", string="Subcontract Picking Type IN"
    )
    sub_out_virtual_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type", string="Subcontract Virtual Picking Type OUT"
    )
    sub_in_virtual_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type", string="Subcontract Virtual Picking Type IN"
    )
    immediate_return_subcontracting = fields.Boolean(
        string="Immediate return subcontracting", default=False
    )
