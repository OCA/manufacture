from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    sub_delivery_workorder_id = fields.Many2one(
        comodel_name="mrp.workorder",
        string="Subcontract Workorder (Is delivery)",
        readonly=True,
        copy=False,
    )
    sub_return_workorder_id = fields.Many2one(
        comodel_name="mrp.workorder",
        string="Subcontract Workorder (Is return)",
        readonly=True,
        copy=False,
    )
    sub_purchase_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        string="Subcontractor purchase order line",
        compute="_compute_sub_purchase_line_id",
        store=True,
    )

    @api.depends("sub_delivery_workorder_id", "sub_return_workorder_id")
    def _compute_sub_purchase_line_id(self):
        for move in self:
            move.sub_purchase_line_id = False
