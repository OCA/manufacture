from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_subcontracting = fields.Boolean(
        string="Subcontracting",
        related="order_type.is_subcontracting",
    )
    subcontract_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Subcontract Location",
        index=True,
    )
    mrp_subcontracting = fields.Boolean(
        string="Mrp subcontracting",
        compute="_compute_mrp_subcontracting",
    )

    def _compute_mrp_subcontracting(self):
        for po in self:
            if po.mapped("order_line").mapped("workorder_id"):
                po.mrp_subcontracting = True
            else:
                po.mrp_subcontracting = False
