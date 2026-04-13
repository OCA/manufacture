from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    subcontract_ok = fields.Boolean(string="Subcontract", default=False)
    purchase_order_line_ids = fields.One2many(
        comodel_name="purchase.order.line",
        inverse_name="workorder_id",
        string="Purchase Order Line",
        readonly=True,
    )
    delivery_move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="sub_delivery_workorder_id",
        string="Delivery Moves",
        readonly=True,
    )
    return_move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="sub_return_workorder_id",
        string="Return Moves",
        readonly=True,
    )
