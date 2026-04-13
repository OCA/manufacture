from odoo import fields, models


class PurchaseOrderType(models.Model):
    _inherit = "purchase.order.type"

    sub_out_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type", string="Subcontract OUT Picking Type"
    )
    sub_in_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type", string="Subcontract IN Picking Type"
    )
    is_subcontracting = fields.Boolean(
        string="Is a subcontracting picking", default=False
    )
    immediate_return_subcontracting = fields.Boolean(
        string="Immediate return subcontracting", default=False
    )
