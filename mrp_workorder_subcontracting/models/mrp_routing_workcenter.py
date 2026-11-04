from odoo import fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    subcontract_ok = fields.Boolean(string="Subcontract", copy=True, default=False)
    subcontractor_partner_ids = fields.Many2many(
        comodel_name="res.partner", string="Subcontractors", copy=True
    )
    subcontract_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Subcontract Service",
        domain=[("type", "=", "service"), ("purchase_ok", "=", True)],
    )
