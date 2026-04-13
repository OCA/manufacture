from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    property_stock_subcontract_location_id = fields.Many2one(
        comodel_name="stock.location", string="Subcontract Location", copy=False
    )
