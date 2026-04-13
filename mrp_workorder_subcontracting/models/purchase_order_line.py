from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    workorder_id = fields.Many2one(
        comodel_name="mrp.workorder", string="Work Order", index=True
    )
    production_id = fields.Many2one(
        related="workorder_id.production_id", string="Manufacturing Order"
    )
